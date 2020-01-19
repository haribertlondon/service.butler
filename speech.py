# -*- coding: utf-8 -*-
#!/usr/bin/env python
import collections
import pyaudio
import time
import math
import audioop
import sys
import mysphinx
import settings
import pluginEcho
import gpio
from settings import isDebug

try:    
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
try:
    from resources.lib.snowboyrpi8 import snowboydetect as snowboydetect#@UnresolvedImport
except Exception as e:
    print("Could not load snowboy", e)


def getByteArray(lst):    
    flat_list = [item for sublist in lst for item in sublist]    
    if (sys.version_info > (3, 0)):
        tmp = bytearray(flat_list)
    else:
        tmp = b"".join(flat_list)
    return tmp    
    

class RingBuffer(object):    
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data): 
        self._buf.append(data)

    def get(self):
        tmp = list(self._buf) #TODO: increase speed?
        self._buf.clear()
        return tmp


class HotwordDetector(object):   
    def __init__(self, decoder_model, sensitivity=[], audio_gain=1.0):

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue
        
        if type(decoder_model) is not list:
            decoder_model = [decoder_model]
        if type(sensitivity) is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)
        
        try:    
            self.detector = snowboydetect.SnowboyDetect(resource_filename=settings.LISTEN_SNOWBOY_RESOURCE, model_str=model_str)
            self.detector.SetAudioGain(audio_gain)
            self.num_hotwords = self.detector.NumHotwords()
            self.num_channels = self.detector.NumChannels()
            self.sample_rate = self.detector.SampleRate()            
    
            if len(decoder_model) > 1 and len(sensitivity) == 1:
                sensitivity = sensitivity*self.num_hotwords
            if len(sensitivity) != 0:
                assert self.num_hotwords == len(sensitivity), "number of hotwords in decoder_model (%d) and sensitivity " + "(%d) does not match" % (self.num_hotwords, len(sensitivity))
            sensitivity_str = ",".join([str(t) for t in sensitivity])
            if len(sensitivity) != 0:
                self.detector.SetSensitivity(sensitivity_str);
        except Exception as e:
            print("Error while loading Snowboy: ", e)
            self.num_channels = 1
            self.sample_rate = settings.LISTEN_SAMPLERATE
            self.num_hotwords = len(settings.LISTEN_SNOWBOY_MODELS)            

        self.chunksize = settings.LISTEN_CHUNKSIZE
        self.seconds_per_buffer = float(self.chunksize) / self.sample_rate
        self.audio_format = pyaudio.paInt16        
        self.ring_buffer = RingBuffer( self.num_channels * self.sample_rate * 5)
        self.audio = pyaudio.PyAudio()
        
        self.sphinxrecognizer = mysphinx.MyRecognizer() #sr.Recognizer()  
        self.sphinxrecognizer.prepare_sphinx2(language = "en-GIT", keyword_entries = settings.LISTEN_SPHINX_KEYWORDS) 

        for mic in enumerate(sr.Microphone.list_microphone_names()):
            print(mic)  
        
        default_info = self.audio.get_default_input_device_info()
        print("Default microphone info ", default_info)
        
        if settings.LISTEN_MIC_INDEX is None:
            settings.LISTEN_MIC_INDEX = default_info['index']            
        
        self.sample_width = pyaudio.get_sample_size(self.audio_format)
        self.energy_threshold = settings.LISTEN_ENERGY_THRESHOLD 
        self.stream_in = self.audio.open( input=True,  output=False, input_device_index=settings.LISTEN_MIC_INDEX, format= self.audio_format, channels=self.num_channels, rate=self.sample_rate, frames_per_buffer=self.chunksize, stream_callback=audio_callback)
        
    def updateTimes(self, energy, chunkSize):
        if energy > self.energy_threshold:
            self.phrase_time += self.seconds_per_buffer*chunkSize 
            self.pause_time = 0                       
        else: 
            if self.phrase_time  > 0:           #only count if something was said before
                self.pause_time += self.seconds_per_buffer*chunkSize             
        
        self.elapsed_time += self.seconds_per_buffer*chunkSize

    def state_phrase(self):
        if self.elapsed_time > settings.LISTEN_PHRASE_MIN_TIME: #reached min time
            if settings.LISTEN_PHRASE_TOTALTIMEOUT is not None and self.elapsed_time > settings.LISTEN_PHRASE_TOTALTIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.elapsed_time, 'Phrase', self.phrase_time, 'Pause: ', self.pause_time)
                return "init"
            else:
                if self.pause_time > settings.LISTEN_PHRASE_PAUSE_THRESHOLD: #wait for pause at the end
                    if self.phrase_time > settings.LISTEN_PHRASE_PUREPHRASETIME:
                        print("Pause ok and Phrase ok", self.pause_time, self.phrase_time)                        
                        return "recognition"
                    else:
                        print("Pause ok, Phrase not Ok", self.pause_time, self.phrase_time)    
                        return "init"    
                else:
                    return "phrase" # wait for more pause at the end of phrase
        else:
            return "phrase"  #still waiting for min time
        
    def hotword_snowboy(self):
        try:
            result = self.detector.RunDetection(self.frame_data)
        except Exception as e:
            print("Snowboy Exception. Reason ", e)
            result = 0
        return result
        
    def hotword_sphinx(self, audio):
        try:       
            a = self.sphinxrecognizer.recognize_sphinx2(audio_data = audio, onlykeywords = True)                    
        except Exception as e:                        
            print("Sphinx Exception. Reason ", e)
            a = ""          
        
        if len(a)>0:
            print("Detected the word: " + a)
            return 1
        else:
            return 0
        
    def state_hotword(self, energy, listening_callback):
        #prepare data for processing
        self.frame_data = getByteArray(self.frames)
        
        #dynamic adjustment
        if settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU>0:
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU) #tau = 4sec => reach 4*6=24sec

        energy2 = audioop.rms(self.frame_data, self.sample_width) 
        energy = energy2*1.0
                
        if (settings.LISTEN_HOTWORD_METHODS in [1,3,4]) and settings.hasSnowboy(): # and energy>self.energy_threshold:
            resultSnowboy = self.hotword_snowboy()
        else:
            resultSnowboy = 0
                    
        if settings.LISTEN_HOTWORD_METHODS in [2,3,4] or not settings.hasSnowboy():
            audio = sr.AudioData(self.frame_data, self.sample_rate, self.sample_width)
            resultSphinx = self.hotword_sphinx(audio)
        else:
            resultSphinx = 0  

        if resultSphinx>0 or resultSnowboy>0:
            print("Snowboy="+ str(resultSnowboy) + "  Sphinx=" + str(resultSphinx) + "  Energy= " + str(energy) +"  Threshold=" + str( self.energy_threshold) )
        #if energy > self.energy_threshold and (settings.LISTEN_HOTWORD_METHODS == 3 and max(resultSnowboy, resultSphinx) > 0 or settings.LISTEN_HOTWORD_METHODS == 4 and resultSnowboy>0 and resultSphinx>0):
        if energy > self.energy_threshold/1.5*1.5 and (resultSnowboy > 0 or resultSphinx > 0):
            print("Keyword detected at time: "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "Snowboy", resultSnowboy, "Sphinx", resultSphinx)

            if listening_callback is not None:
                listening_callback()

            gpio.setLedState(gpio.LED_RED, gpio.LED_ON, gpio.ONLY_ONE_LED)

            self.pause_time = 0.0
            self.elapsed_time = 0.0
            self.phrase_time = 0.0    
            self.startTime_for_tictoc = time.time()
            return "phrase"
        else:
            return "hotword"

    def state_init(self):    
        print("State-Init")    
        self.frames[:]=[]
        self.framesBufferSize = 0
        self.elapsed_time = 0
        self.startTime_for_tictoc = time.time()
        gpio.setMultipleLed(gpio.ALL_LEDS, gpio.LED_OFF)       
        return "silence"
    
    def applyLowPassFilter(self, energy, tau):        
        damping = math.exp( - self.cycleTime / tau ) #mit damping=exp(-0.023/tau) self.seconds_per_buffer = 0.023 
        target_energy = energy * settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_RATIO
        self.energy_threshold = self.energy_threshold * damping + target_energy * (1.0 - damping) #y(n) = damping*y(n-1) + (1-damping)*x(n)
    
    def state_adjustSilence(self, energy):
        # adjust energy threshold until a phrase starts               
        if self.elapsed_time > settings.LISTEN_ADJUSTSILENCE_DURATION:
            print("Defined silence threshold ", self.energy_threshold)
            self.startTime_for_tictoc = time.time() 
            self.elapsed_time = 0
            self.phrase_time = 0
            return "hotword"
        else:
            # dynamically adjust the energy threshold using asymmetric weighted average            
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_FAST_TAU)
            return "silence"
    
    def state_recognition(self, detected_callback):
        
        response = {"error": None, "transcription": None }
        gpio.setLedState(gpio.LED_YELLOW, gpio.LED_ON, gpio.ONLY_ONE_LED)        
        try:
            print("Starting speech recognition...")
            #self.frame_data = getByteArray(self.frames)
            #audio = sr.AudioData(self.frame_data, self.sample_rate, self.sample_width)
            #pluginEcho.echoStoreWav(audio, "original.wav")            

            #cut pause at the end of buffer (increases recognition speed)
            bufferLenOfPause = (int)( (settings.LISTEN_PHRASE_PAUSE_THRESHOLD-0.2) / self.seconds_per_buffer) 
            print("bufferLenOfPause: "+str(bufferLenOfPause)+" von "+str(len(self.frames)))
            if bufferLenOfPause> 0 and bufferLenOfPause < len(self.frames):
                self.frames = self.frames[:-bufferLenOfPause]
            print("New bufferLen: "+str(len(self.frames)))
            
            #prepare data for processing
            self.frame_data = getByteArray(self.frames)
            
            audio = sr.AudioData(self.frame_data, self.sample_rate, self.sample_width)
            
            recognizer = sr.Recognizer()    
            response["transcription"] = recognizer.recognize_google(audio, key=None, language=settings.LISTEN_LANGUAGE)        
            
            print("Detected: ", response["transcription"])
            try:
                print(response["transcription"].encode("utf8")) #print("Print as utf8 in python 2")
            except Exception as e:
                print(e)

        except sr.RequestError as e:
            response["error"] = "API unavailable " +  str(e) # API was unreachable or unresponsive
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech" # speech was unintelligible
        
        if isDebug():# or True:    
            pluginEcho.echoStoreWav(audio) 
            
        if detected_callback: #and not settings.isDebug():
            detected_callback(response, audio)  

        return "end"
 
    def start(self, detected_callback=None, listening_callback = None):
        state = "init"
        self.frames = []
        self.framesBufferSize = 0
        lastTime = 0        
        self.startTime_for_tictoc = time.time()
        self.phrase_time = 0
        self.pause_time = 0
        self.elapsed_time = 0
        self.cycleTime = self.seconds_per_buffer * 1.1        
        while True:            
            lastState = state
            
            #get data from other thread            
            chunk = self.ring_buffer.get()
            if len(chunk) == 0:                
                time.sleep(self.cycleTime) #wait for buffer to be filled
                continue
            
            #analyze one chunk
            dataArray = getByteArray(chunk)
            energy = audioop.rms(dataArray, self.sample_width) 
            
            self.updateTimes(energy, len(chunk))
            
            #whole frame buffer
            self.frames.extend(chunk)          
            dur = len(self.frames)*self.seconds_per_buffer #keep length of buffer small 
            
            #reduce buffer length as ring buffer
            if state == "phrase" or state == "recognition": #here, we need a longer buffer
                maxFrameLen = settings.LISTEN_PHRASE_TOTALTIMEOUT + settings.LISTEN_HOTWORD_DURATION + 1.0
            else:
                maxFrameLen = settings.LISTEN_HOTWORD_DURATION 
            newLength = (int)(maxFrameLen/self.seconds_per_buffer)
            
            if len(self.frames) > newLength:            
                self.frames = self.frames[-newLength:] 
            
                
            
            #state machine
            if state == "init":
                state = self.state_init()
            elif state == "silence":
                state = self.state_adjustSilence(energy)
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
            if lastState != state or abs(self.elapsed_time-lastTime)>settings.LISTEN_VERBOSE_TIMEOUT:
                lastTime = self.elapsed_time
                print('Current state', state, "Buffer: ", len(self.frames), ' Energy:', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.startTime_for_tictoc,1)), 'Elapsed: ', round(self.elapsed_time,2), 'Pause: ', round(self.pause_time,2), 'Phrase: ', round(self.phrase_time,2) )

        print("finished.")

    def terminate(self):       
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()

def run(sensitivity=0.5, detected_callback = None, audio_gain = 1.0, listening_callback = None):
    detector = HotwordDetector(decoder_model = settings.LISTEN_SNOWBOY_MODELS, sensitivity=sensitivity, audio_gain = audio_gain)    
    print('Listening... ')    
    detector.start(detected_callback=detected_callback, listening_callback = listening_callback)
    detector.terminate()

if __name__ == '__main__': 
    run()
    
