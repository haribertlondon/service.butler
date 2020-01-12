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
import pluginKodi

try:    
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
try:
    from resources.lib.snowboyrpi8 import snowboydetect as snowboydetect#@UnresolvedImport
except Exception as e:
    print("Could not load snowboy", e)


class RingBuffer(object):    
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):        
        self._buf.extend(data)

    def get(self):
        if (sys.version_info > (3, 0)):
            tmp = bytearray(self._buf)
        else:
            tmp = b"".join(self._buf)
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
        
    def updateTimes(self, energy):
        if energy > self.energy_threshold:
            self.phrase_time += self.seconds_per_buffer 
            self.pause_time = 0                       
        else: 
            if self.phrase_time  > 0:           #only count if something was said before
                self.pause_time += self.seconds_per_buffer             
        
        self.elapsed_time += self.seconds_per_buffer

    def state_phrase(self, data, energy):
        
        self.updateTimes(energy)
            
        self.frames.append(data)
            
        if self.elapsed_time > settings.LISTEN_PHRASE_MIN_TIME: #reached min time
            if settings.LISTEN_PHRASE_TOTALTIMEOUT is not None and self.elapsed_time > settings.LISTEN_PHRASE_TOTALTIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.elapsed_time, 'Phrase', self.phrase_time, 'Pause: ', self.pause_time)
                return ("init", None)
            else:
                if self.pause_time > settings.LISTEN_PHRASE_PAUSE_THRESHOLD: #wait for pause at the end
                    if self.phrase_time > settings.LISTEN_PHRASE_PUREPHRASETIME:
                        print("Pause ok and Phrase ok", self.pause_time, self.phrase_time)
                        frame_data = b"".join(self.frames)
                        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
                        return ("recognition", audio)
                    else:
                        print("Pause ok, Phrase not Ok", self.pause_time, self.phrase_time)    
                        return ("init", None)    
                else:
                    return ("phrase", None) # wait for more pause at the end of phrase
        else:
            return ("phrase", None) #still waiting for min time
        
    def hotword_sphinx(self, _):
        frame_data = b"".join(self.frames)
        
        dur = len(frame_data)*1.0000001/self.sample_rate/self.sample_width
        #print(dur)
        targetDuration = 0.8
        newLength = (int)(len(self.frames)*targetDuration/dur)
        if newLength < len(self.frames):            
            self.frames = self.frames[-newLength:]
            frame_data = b"".join(self.frames)
                       
        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
        
        try:       
            a = self.sphinxrecognizer.recognize_sphinx2(audio_data = audio, onlykeywords = True)                    
        except Exception as e:                        
            print("Exception ", e)
            a = ""          
        
        if len(a)>0:
            print("Detected words", a)
            return 1
        else:
            return 0
        
    def state_snowboy(self, data, energy):
            
        #minN = (int)(0.4/self.seconds_per_buffer) #keeps some time 0.5sec before the phrase
        #if len(self.frames) > minN:
        #    self.frames = self.frames[-minN:] #keep last N frames                    
        
        self.frames.append(data)  
        
        try:
            if settings.LISTEN_SPHINX_ACTIVE:
                raise Exception("We should use sphinx")  
                      
            ans = self.detector.RunDetection(data)    #TODO: ++++++++++++++++++++++maybe not data but whole buffer?++++++++++++++++++++++                        
        except Exception as e:
            if self.elapsed_time == 0:
                print("Failed to run snowboy. Wait for start of phrase by energy", e)                
            
            self.updateTimes(energy)
            #if self.pause_time > 1.0: #throw phrase away if pause was too long
            #    self.phrase_time = 0
            #if self.phrase_time > 0.25:                
            #    ans = 1
            #else: 
            #    ans = 0
            ans = self.hotword_sphinx(data)
        #dynamic adjustment
        if settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU>0:
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU) #tau = 4sec => reach 4*6=24sec
                      
        self.elapsed_time += self.seconds_per_buffer
              
        if ans == -1:
            print("Error initializing streams or reading audio data")
            return "error"
        elif ans > 0:                
            print("Keyword " + str(ans) + " detected at time: "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
            pluginKodi.kodiShowMessage("Listening...")

            self.pause_time = 0.0
            self.elapsed_time = 0.0
            self.phrase_time = 0.0    
            self.startTime_for_tictoc = time.time()
            return "phrase"
        else:
            return "snowboy"

    def state_init(self):    
        print("State-Init")    
        self.frames[:]=[]
        self.elapsed_time = 0
        self.startTime_for_tictoc = time.time()
        return "silence"
    
    def applyLowPassFilter(self, energy, tau):
        #mit damping=exp(-0.023/tau) self.seconds_per_buffer = 0.023
        damping = math.exp( - self.cycleTime / tau ) 
        target_energy = energy * settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_RATIO
        self.energy_threshold = self.energy_threshold * damping + target_energy * (1.0 - damping)
        #y(n) = damping*y(n-1) + (1-damping)*x(n)      
    
    def state_adjustSilence(self, energy):
        # adjust energy threshold until a phrase starts       
        self.elapsed_time += self.seconds_per_buffer
        if self.elapsed_time > settings.LISTEN_ADJUSTSILENCE_DURATION:
            print("Defined silence threshold ", self.energy_threshold)
            self.startTime_for_tictoc = time.time() 
            self.elapsed_time = 0
            self.phrase_time = 0
            return "snowboy"
        else:
            # dynamically adjust the energy threshold using asymmetric weighted average            
            self.applyLowPassFilter(energy, settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_FAST_TAU)
            return "silence"
    
    def state_storeWav(self, audio):
        
        if settings.isDebug():
            pluginEcho.echoStoreWav(audio)
            #pluginEcho.echoPlayWav()
        
        return "end"
    
    def state_recognition(self, audio, detected_callback):
        
        response = {"error": None, "transcription": None }
    
        try:
            if settings.LISTEN_LANGUAGE == "":
                settings.LISTEN_LANGUAGE = None
            
            print("Starting speech recognition...")
            
            recognizer = sr.Recognizer()    
            response["transcription"] = recognizer.recognize_google(audio, key=None, language=settings.LISTEN_LANGUAGE)        
            #response["transcription"] = recognizer.recognize_wit(audio, key='6PKAY4NP4U4VJPBJAEHSWV7JS5HWTSQE')            
            #response["transcription"] = recognizer.recognize_bing(audio, key='912b8cb579f74a01aba54691b1d9c671')#, language=settings.LISTEN_LANGUAGE)            
            
            print("Detected: ", response["transcription"])
            try:
                print("Print as utf8 in python 2")
                print(response["transcription"].encode("utf8"))
            except Exception as e:
                print(e)

            
        except sr.RequestError as e:
            # API was unreachable or unresponsive        
            response["error"] = "API unavailable " +  str(e)
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"     
            
        if detected_callback: #and not settings.isDebug():
            detected_callback(response, audio)  

        return "wav"
 
    def start(self, detected_callback=None):       
        state = "init"
        self.frames = []
        lastTime = 0        
        self.startTime_for_tictoc = time.time()
        self.phrase_time = 0
        self.pause_time = 0
        self.cycleTime = self.seconds_per_buffer * 1.5
        while True:            
                        
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(self.cycleTime) #wait for buffer to be filled               
                continue
            
            energy = audioop.rms(data, self.sample_width) 
            
            lastState = state
            
            if state == "init":
                state = self.state_init()
            elif state == "silence":
                state = self.state_adjustSilence(energy)
            elif state == "snowboy":
                state = self.state_snowboy(data, energy)
            elif state ==  "phrase":
                (state, audio) = self.state_phrase(data, energy)
            elif state == "recognition":
                state = self.state_recognition(audio, detected_callback)
            elif state == "wav":
                state = self.state_storeWav(audio)
            elif state == "end":
                state = "init" #start all over again
            else:
                raise Exception("Unknown state ", state)
                
                
            if lastState != state or abs(self.elapsed_time-lastTime)>settings.LISTEN_VERBOSE_TIMEOUT:
                lastTime = self.elapsed_time
                print('    Current state', state, "Buffer: ", len(self.frames), ' Energy:', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.startTime_for_tictoc,1)), 'Elapsed: ', round(self.elapsed_time,2), 'Pause: ', round(self.pause_time,2), 'Phrase: ', round(self.phrase_time,2) )

        print("finished.")

    def terminate(self):       
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()

def run(sensitivity=0.5, detected_callback = None, audio_gain = 1.0):    
    detector = HotwordDetector(decoder_model = settings.LISTEN_SNOWBOY_MODELS, sensitivity=sensitivity, audio_gain = audio_gain)    
    print('Listening... ')    
    detector.start(detected_callback=detected_callback)
    detector.terminate()

if __name__ == '__main__': 
    run()
    
