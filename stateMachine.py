import speech
import settings
import time
import gpio

class TimeTracker():
    def __init__(self, seconds_per_buffer):
        self.seconds_per_buffer = seconds_per_buffer
        self.reset()
        
    def reset(self):                
        self.elapsed_time = 0.0
        self.time_hotword_detected = 0.0
        self.time_since_hotword = 0.0    
        self.pause_time_after_phrase = 0.0
        self.high_energy_time_since_hotword = 0.0
        self.high_energy_time = 0.0
        self.startTime_for_tictoc = time.time()
        
    def update(self, infos):
        self.reset()
        for info in infos:
            self.updateChunk(info)        
        
    def updateChunk(self, info): 
        (isEnergy, isHotword) = info 
        
        seconds = self.seconds_per_buffer  
        self.elapsed_time += seconds
        
        if (isHotword or self.time_since_hotword > 0.0):
            self.time_since_hotword += seconds
            if isEnergy:
                self.high_energy_time_since_hotword += seconds
        else:
            self.time_hotword_detected += seconds
             
        if isEnergy:
            self.high_energy_time += seconds
            self.pause_time_after_phrase = 0                       
        else: 
            if self.high_energy_time  > 0:           #only count if something was said before
                self.pause_time_after_phrase += seconds            


class HotwordDetectorStateMachine(speech.HotwordDetector): 
       
    def state_startup(self):    
        print("State-Startup")    
        self.tracker.reset()
        return "silence"
    
    def state_adjustSilence(self, energy):
        # adjust energy threshold until a phrase starts               
        if self.tracker.elapsed_time+self.seconds_per_buffer > settings.LISTEN_ADJUSTSILENCE_DURATION:
            print("Defined silence threshold ", self.energy_threshold)
            return "init"
        else:
            # dynamically adjust the energy threshold using asymmetric weighted average            
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_FAST_TAU)
            return "silence" 
        
    def state_init(self):    
        print("State-Init")
        gpio.setMultipleLed(gpio.ALL_LEDS, gpio.LED_OFF)
        self.resetFrameBuffer()
        if self.precise_engine: #clear buffer from last run by restarting engine
            self.precise_engine.stop()
            self.precise_engine.start()
        return "hotword" 
    
    def state_hotword(self, energy, listening_callback):

        #dynamic adjustment
        if settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU>0:
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU) #tau = 4sec => reach 4*6=24sec        
                
        if (1 in settings.LISTEN_HOTWORD_METHODS) and settings.hasSnowboy(): # and energy>self.energy_threshold:
            resultSnowboy = self.hotword_snowboy()
        else:
            resultSnowboy = 0
                    
        if (2 in settings.LISTEN_HOTWORD_METHODS) or not settings.hasSnowboy():
            resultSphinx = self.hotword_sphinx()
        else:
            resultSphinx = 0  
			
        if (3 in settings.LISTEN_HOTWORD_METHODS):
            resultPrecise = self.hotword_precise()
        else:
            resultPrecise = 0

        if resultSphinx>0 or resultSnowboy>0 or resultPrecise > 0:
            self.infos[-1] = (self.infos[-1][0], True) 
            print("Snowboy="+ str(resultSnowboy) + "  Sphinx=" + str(resultSphinx)  + "  Precise=" + str(resultPrecise) + "  Energy= " + str(energy) +"  Threshold=" + str( self.energy_threshold)+ " Time: "+str(self.tracker.high_energy_time) +"sec > "+ str(settings.LISTEN_HOTWORD_MIN_DURATION )+"sec")
        
        if (self.tracker.high_energy_time > settings.LISTEN_HOTWORD_MIN_DURATION) and (resultPrecise > 0 or resultSnowboy > 0 or resultSphinx > 0):
            print("Keyword detected at time: "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "Snowboy", resultSnowboy, "Sphinx", resultSphinx, "Precise", resultPrecise)
            
            if listening_callback is not None:
                listening_callback()

            gpio.setLedState(gpio.LED_RED, gpio.LED_ON, gpio.ONLY_ONE_LED)

            return "phrase"
        else:
            return "hotword"


    def state_phrase(self):

        if self.tracker.elapsed_time > settings.LISTEN_PHRASE_TOTALTIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.tracker.elapsed_time, 'Phrase', self.tracker.high_energy_time, 'Pause: ', self.tracker.pause_time_after_phrase)
                return "init"
        elif self.tracker.pause_time_after_phrase > settings.LISTEN_PAUSE_TIME_AFTER_PHRASE_THRESHOLD:
            
            self.tracker.energy_percentage = max(0, (self.tracker.high_energy_time_since_hotword+1e-50) / (self.tracker.time_since_hotword-settings.LISTEN_PAUSE_TIME_AFTER_PHRASE_THRESHOLD+1e-40) )
             
            checkPause = self.tracker.pause_time_after_phrase > settings.LISTEN_PAUSE_TIME_AFTER_PHRASE_THRESHOLD
            checkPhrase = self.tracker.high_energy_time_since_hotword > settings.LISTEN_HIGH_ENERGY_TIME_SINCE_HOTWORD_THRESHOLD  
            checkTotal = self.tracker.time_since_hotword > settings.LISTEN_TIME_SINCE_HOTWORD_THRESHOLD    
            checkPercentage = self.tracker.energy_percentage > settings.LISTEN_PHRASE_PERCENTAGE

            if settings.isDebug():
                self.storeWav(settings.LISTEN_WRITEWAV, None, 0)
            
            print("Elapsed Time     ", self.tracker.elapsed_time)
            print("Checking Pause:  ", checkPause,      '   ', self.tracker.pause_time_after_phrase , '>', settings.LISTEN_PAUSE_TIME_AFTER_PHRASE_THRESHOLD)
            print("Checking Phrase: ", checkPhrase,     '   ', self.tracker.high_energy_time_since_hotword , '>', settings.LISTEN_HIGH_ENERGY_TIME_SINCE_HOTWORD_THRESHOLD, self.tracker.high_energy_time)
            print("Checking Total:  ", checkTotal,      '   ', self.tracker.time_since_hotword ,'>', settings.LISTEN_TIME_SINCE_HOTWORD_THRESHOLD)
            print("Checking Percent:", checkPercentage, '   ', self.tracker.energy_percentage ,'>', settings.LISTEN_PHRASE_PERCENTAGE)
            
            if checkPhrase and checkTotal and checkPercentage:                
                return "recognition"
            else:                
                return "init"    
        else:
            return "phrase" # wait for more pause at the end of phrase
        

    
    def state_recognition(self, detected_callback):

        gpio.setLedState(gpio.LED_YELLOW, gpio.LED_ON, gpio.ONLY_ONE_LED)        
        
        print("Starting speech recognition...")

        #cut pause at the end of buffer (increases recognition speed)
        self.cutRightFrames(settings.LISTEN_PAUSE_TIME_AFTER_PHRASE_THRESHOLD-0.2)
        print("New bufferLen: "+str(len(self.frames)))
        
        response = self.recognize()
        
        print("Detected: ", response["transcription"])
        try:
            if response["transcription"] is not None:
                print(response["transcription"].encode("utf8")) #print("Print as utf8 in python 2")
        except Exception as e:
            print(e)

        if detected_callback: #and not settings.isDebug():
            foundMatch = detected_callback(response)
            
            if True:#foundMatch and settings.isDebug():
                if foundMatch:
                    self.storeWav(settings.LISTEN_TRAINDATA_PATH+'wake-word/wake-word_', self.tracker.time_hotword_detected + 0.5, 3000) #store 
                else:
                    self.storeWav(settings.LISTEN_TRAINDATA_PATH+'not-wake-word/not-wake-word_', self.tracker.time_hotword_detected + 0.5, 3000) #store
                    
                if foundMatch:
                    self.storeWav(settings.LISTEN_TRAINDATA_PATH+'full-phrase-good/full-phrase-good_', None, 3000) #store  
                else:
                    self.storeWav(settings.LISTEN_TRAINDATA_PATH+'full-phrase-fail/full-phrase-fail_', None, 3000) #store

        return "end"
 
    def start(self, detected_callback=None, listening_callback = None):
        state = "startup"
                
        self.tracker = TimeTracker(self.seconds_per_buffer)        
 
        self.cycleTime = self.seconds_per_buffer * 1.01

        while True:

            #reduce buffer length as ring buffer
            if state == "phrase" or state == "recognition": #here, we need a longer buffer
                maxFrameLen = settings.LISTEN_PHRASE_TOTALTIMEOUT + settings.LISTEN_HOTWORD_MAX_DURATION + 1.0
            elif state == "hotword":
                maxFrameLen = settings.LISTEN_HOTWORD_MAX_DURATION
            elif state == "silence":
                maxFrameLen = settings.LISTEN_ADJUSTSILENCE_DURATION 
            else:
                maxFrameLen = 0
                
            (energy, chunkSize) = self.updateFrames(maxFrameLen)
            
            if chunkSize == 0:
                time.sleep(self.cycleTime) #wait for buffer to be filled
                continue
            
            self.tracker.update(self.infos)
            
            try:
                #state machine
                lastState = state
                if state == "startup":
                    state = self.state_startup()
                elif state == "silence":
                    state = self.state_adjustSilence(energy)
                elif state == "init":
                    state = self.state_init()
                elif state == "hotword":            
                    state = self.state_hotword(energy, listening_callback)
                elif state ==  "phrase":
                    state = self.state_phrase()
                elif state == "recognition":
                    state = self.state_recognition(detected_callback)
                elif state == "end":
                    state = "init" #start all over again
                else:
                    raise Exception("Unknown state ", state)
                    
                #print out
                if lastState != state:# or settings.isDebug():
                    print('Current state', state, "Buffer: ", len(self.frames), ' Energy:', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.tracker.startTime_for_tictoc,1)), 'Elapsed: ', round(self.tracker.elapsed_time,2), 'Pause: ', round(self.tracker.pause_time_after_phrase,2), 'Phrase: ', round(self.tracker.high_energy_time,2) )
            except Exception as e:
                print("Fatal error in state machine. Restart...")
                print(e)
                time.sleep(3)
                state = "startup"
                raise

        print("finished.")
