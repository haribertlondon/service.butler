import speech
import settings
import time
import gpio

class TimeTracker():
    def __init__(self, seconds_per_buffer):
        self.seconds_per_buffer = seconds_per_buffer
        self.reset()
        
    def reset(self):
        self.pause_time_after_phrase = 0.0
        self.total_pause_time = 0.0
        self.elapsed_time = 0.0
        self.total_time_since_last_hotword = 0.0    
        self.pure_phrase_time = 0.0
        self.startTime_for_tictoc = time.time()
        
    def update(self, infos, energy_threshold):
        self.reset()
        self.energy_threshold = energy_threshold
        for info in infos:
            self.updateChunk(info)
        
    def updateChunk(self, info): 
        (energy, isHotword) = info 
        
        seconds = self.seconds_per_buffer  
        self.elapsed_time += seconds
        
        if (isHotword or self.total_time_since_last_hotword > 0.0):
            self.total_time_since_last_hotword += seconds
             
        if energy > self.energy_threshold:
            self.pure_phrase_time += seconds
            self.pause_time_after_phrase = 0                       
        else: 
            if self.pure_phrase_time  > 0:           #only count if something was said before
                self.pause_time_after_phrase += seconds
            self.total_pause_time += seconds            


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
        return "hotword" 
    
    def state_hotword(self, energy, listening_callback):

        #dynamic adjustment
        if settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU>0:
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU) #tau = 4sec => reach 4*6=24sec        
                
        if (settings.LISTEN_HOTWORD_METHODS in [1,3,4]) and settings.hasSnowboy(): # and energy>self.energy_threshold:
            resultSnowboy = self.hotword_snowboy()
        else:
            resultSnowboy = 0
                    
        if settings.LISTEN_HOTWORD_METHODS in [2,3,4] or not settings.hasSnowboy():
            resultSphinx = self.hotword_sphinx()
        else:
            resultSphinx = 0  

        if resultSphinx>0 or resultSnowboy>0:
            self.infos[-1] = (self.infos[-1][0], True) 
            print("Snowboy="+ str(resultSnowboy) + "  Sphinx=" + str(resultSphinx) + "  Energy= " + str(energy) +"  Threshold=" + str( self.energy_threshold)+ " Time: "+str(self.tracker.pure_phrase_time) +"sec > "+ str(settings.LISTEN_HOTWORD_MIN_DURATION )+"sec")
            if settings.isDebug():
                self.storeWav()
                print("Stored to file")
        
        if (self.tracker.pure_phrase_time > settings.LISTEN_HOTWORD_MIN_DURATION) and (resultSnowboy > 0 or resultSphinx > 0):
            print("Keyword detected at time: "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "Snowboy", resultSnowboy, "Sphinx", resultSphinx)
            
            if listening_callback is not None:
                listening_callback()

            gpio.setLedState(gpio.LED_RED, gpio.LED_ON, gpio.ONLY_ONE_LED)

            return "phrase"
        else:
            return "hotword"


    def state_phrase(self):

        if self.tracker.elapsed_time > settings.LISTEN_PHRASE_TOTALTIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.tracker.elapsed_time, 'Phrase', self.tracker.pure_phrase_time, 'Pause: ', self.tracker.pause_time_after_phrase)
                return "init"
        elif self.tracker.pause_time_after_phrase > settings.LISTEN_PHRASE_PAUSE_THRESHOLD: #wait for pause at the end
            if self.tracker.pure_phrase_time > settings.LISTEN_PUREPHRASE_MIN_TIME  and self.tracker.total_time_since_last_hotword > settings.LISTEN_FULLPHRASE_MIN_TIME:
                print("Pause ok and Phrase     ok  Pause: "+str( self.tracker.pause_time_after_phrase) +' || '+str(self.tracker.pure_phrase_time) + ' > '+str(settings.LISTEN_PUREPHRASE_MIN_TIME  )+'  ||  '+str(self.tracker.total_time_since_last_hotword )+ ' > '+ str(settings.LISTEN_FULLPHRASE_MIN_TIME))                        
                return "recognition"
            else:
                print("Pause ok and Phrase not ok Pause: "+str( self.tracker.pause_time_after_phrase) +' || '+str(self.tracker.pure_phrase_time) + ' > '+str(settings.LISTEN_PUREPHRASE_MIN_TIME  )+'  ||  '+str(self.tracker.total_time_since_last_hotword )+ ' > '+ str(settings.LISTEN_FULLPHRASE_MIN_TIME))    
                return "init"    
        else:
            return "phrase" # wait for more pause at the end of phrase
        

    
    def state_recognition(self, detected_callback):

        gpio.setLedState(gpio.LED_YELLOW, gpio.LED_ON, gpio.ONLY_ONE_LED)        
        
        print("Starting speech recognition...")

        #cut pause at the end of buffer (increases recognition speed)
        self.cutRightFrames(settings.LISTEN_PHRASE_PAUSE_THRESHOLD-0.2)
        print("New bufferLen: "+str(len(self.frames)))
        
        response = self.recognize()
        
        print("Detected: ", response["transcription"])
        try:
            print(response["transcription"].encode("utf8")) #print("Print as utf8 in python 2")
        except Exception as e:
            print(e)

        if detected_callback: #and not settings.isDebug():
            detected_callback(response)  

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
            
            self.tracker.update(self.infos, self.energy_threshold)
            
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
                print('Current state', state, "Buffer: ", len(self.frames), ' Energy:', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.tracker.startTime_for_tictoc,1)), 'Elapsed: ', round(self.tracker.elapsed_time,2), 'Pause: ', round(self.tracker.pause_time_after_phrase,2), 'Phrase: ', round(self.tracker.pure_phrase_time,2) )

        print("finished.")