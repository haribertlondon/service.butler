# -*- coding: utf-8 -*-
#!/usr/bin/env python

import collections
import pyaudio
import time
import audioop
import sys
import settings
import pluginEcho
try:    
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
try:
    import snowboydetect #@UnresolvedImport
except:
    print("Could not load snowboy")



class RingBuffer(object):    
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):        
        self._buf.extend(data)

    def get(self):
        tmp = bytearray(self._buf)
        self._buf.clear()
        return tmp


class HotwordDetector(object):   
    def __init__(self, decoder_model, resource=".", sensitivity=[], audio_gain=1.0):

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
            self.detector = snowboydetect.SnowboyDetect(resource_filename=resource, model_str=model_str)
            self.detector.SetAudioGain(audio_gain)
            self.num_hotwords = self.detector.NumHotwords()
            self.num_channels = self.detector.NumChannels()
            self.sample_rate = self.detector.SampleRate()
            self.bit_per_sample = self.detector.BitsPerSample()
    
            if len(decoder_model) > 1 and len(sensitivity) == 1:
                sensitivity = sensitivity*self.num_hotwords
            if len(sensitivity) != 0:
                assert self.num_hotwords == len(sensitivity), "number of hotwords in decoder_model (%d) and sensitivity " + "(%d) does not match" % (self.num_hotwords, len(sensitivity))
            sensitivity_str = ",".join([str(t) for t in sensitivity])
            if len(sensitivity) != 0:
                self.detector.SetSensitivity(sensitivity_str);
        except:
            self.num_channels = 1
            self.sample_rate = 44100
            self.num_hotwords = 1            

        self.chunksize = settings.LISTEN_CHUNKSIZE
        self.seconds_per_buffer = float(self.chunksize) / self.sample_rate
        self.audio_format = pyaudio.paInt16        
        self.ring_buffer = RingBuffer( self.num_channels * self.sample_rate * 5)
        self.audio = pyaudio.PyAudio()
        self.sample_width = pyaudio.get_sample_size(self.audio_format)
        self.stream_in = self.audio.open( input=True,  output=False, format= self.audio_format, channels=self.num_channels, rate=self.sample_rate, frames_per_buffer=self.chunksize, stream_callback=audio_callback)

    def state_phrase(self, data, frames, energy):        
        if energy > settings.LISTEN_ENERGY_THRESHOLD:
            self.phrase_time += self.seconds_per_buffer 
            self.pause_time = 0                       
        else: 
            if self.phrase_time  > 0:           #only count if something was said before
                self.pause_time += self.seconds_per_buffer 
            else:
                minN = round(0.5/self.seconds_per_buffer) #keeps some time 0.5sec before the phrase                
                if len(frames) > minN:
                    frames = frames[-minN:] #keep last N frames       
        
        self.elapsed_time += self.seconds_per_buffer
        
        print("State-Phrase ", len(frames), ' ', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.startTime_for_tictoc,1)), 'Elapsed: ', round(self.elapsed_time,2), 'Pause: ', round(self.pause_time,2), 'Phrase: ', round(self.phrase_time,2) )
            
        frames.append(data)
            
        if self.elapsed_time > settings.LISTEN_PHRASE_MIN_TIME: #reached min time
            if settings.LISTEN_PHRASETIMEOUT is not None and self.elapsed_time > settings.LISTEN_PHRASETIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.elapsed_time) 
                frames.clear()               
                return ("init", None)
            else:
                if self.pause_time > settings.LISTEN_PAUSE_THRESHOLD: #wait for pause at the end
                    if self.phrase_time > settings.LISTEN_PURE_PHRASE_TIME:
                        print("Pause ok and Phrase ok", self.pause_time, self.phrase_time)
                        frame_data = b"".join(frames)
                        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
                        return ("recognition", audio)
                    else:
                        print("Pause ok, Phrase not Ok", self.pause_time, self.phrase_time)    
                        return ("init", None)    
                else:
                    return ("phrase", None) # wait for more pause at the end of phrase
        else:
            return ("phrase", None) #still waiting for min time           
        
    def state_snowboy(self, data, frames):
        print("State-Snowboy")
        try:
            ans = self.detector.RunDetection(data)                
        except:
            ans = 1
        
        frames.append(data)        
        if ans == -1:
            print("Error initializing streams or reading audio data")
            return "error"
        elif ans > 0:                
            print("Keyword " + str(ans) + " detected at time: "+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
            self.pause_time = 0.0
            self.elapsed_time = 0.0
            self.phrase_time = 0.0
            self.energy_threshold = settings.LISTEN_ENERGY_THRESHOLD            
            self.startTime_for_tictoc = time.time()
            return "phrase"
        else:
            frames.clear() #remove unwanted buffer        
            return "snowboy"

    def state_init(self, frames):    
        print("State-Init")    
        frames.clear()
        return "calibrate"
    
    def state_calibrate(self,energy):
        print("State-Calibrate")
        return "snowboy"
    
    def state_storeWav(self, audio):
        pluginEcho.echoStoreWav(audio)
        return "end"
    
    def state_recognition(self, audio, detected_callback):
        print("State-Recognition")        
        
        response = {"error": None, "transcription": None }
    
        try:
            if settings.LISTEN_LANGUAGE == "":
                settings.LISTEN_LANGUAGE = None
            
            print("Starting speech recognition...")
            
            recognizer = sr.Recognizer()    
            response["transcription"] = recognizer.recognize_google(audio, key=None, language=settings.LISTEN_LANGUAGE)        
            #response["transcription"] = recognizer.recognize_wit(audio, key='6PKAY4NP4U4VJPBJAEHSWV7JS5HWTSQE')
            #response["transcription"] = recognizer.recognize_wit(audio, key='6PKAY4NP4U4VJPBJAEHSWV7JS5HWTSQE')
            #response["transcription"] = recognizer.recognize_bing(audio, key='912b8cb579f74a01aba54691b1d9c671')#, language=settings.LISTEN_LANGUAGE)
            #response["transcription"] = recognizer.recognize_sphinx(audio, language='de-DE') #settings.LISTEN_LANGUAGE)#, language=settings.LISTEN_LANGUAGE)
            
            print("Detected: ", response["transcription"])
            
        except sr.RequestError as e:
            # API was unreachable or unresponsive        
            response["error"] = "API unavailable " +  str(e)
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"     
            
        if detected_callback:
            detected_callback(response, audio)  

        return "wav"

    def start(self, detected_callback=None, interrupt_check=lambda: False, sleep_time=0.03):       
        state = "init"
        frames = []
        audio = None
        while True:            
                        
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time) #wait for buffer
                continue
            
            energy = audioop.rms(data, self.sample_width) 
            
            if state == "init":
                state = self.state_init(frames)
            elif state == "calibrate":
                state = self.state_calibrate(energy)
            elif state == "snowboy":
                state = self.state_snowboy(data, frames)
            elif state ==  "phrase":
                (state, audio) = self.state_phrase(data, frames, energy)
            elif state == "recognition":
                state = self.state_recognition(audio, detected_callback)
            elif state == "wav":
                state = self.state_storeWav(audio)
            elif state == "end":
                state = "init" #start all over again
            else:
                print("Unknown state ", state)
                sys.exit()

        print("finished.")

    def terminate(self):       
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()

def run(sensitivity=0.5, sleep = 0.03, detected_callback = None, audio_gain = 1.0):    
    detector = HotwordDetector(decoder_model = settings.LISTEN_SNOWBOY_MODELS, resource = settings.LISTEN_SNOWBOY_RESOURCE, sensitivity=sensitivity, audio_gain = audio_gain)
    print('Listening... ')    
    detector.start(detected_callback=detected_callback, interrupt_check=None, sleep_time=sleep)
    detector.terminate()

if __name__ == '__main__': 
    run()
    