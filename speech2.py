# -*- coding: utf-8 -*-
#!/usr/bin/env python

import collections
import pyaudio
import audioop
import settings
import pluginEcho
try:
    import snowboydetect
except:
    print("Could not load snowboy")
import time


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
            self.pause_time += self.seconds_per_buffer            
        
        self.elapsed_time += self.seconds_per_buffer
        
        print("State-Phrase ", len(frames), ' ', str(round(energy,2)), '>', str(round(self.energy_threshold,2)), 'Time: ',str(round(time.time() - self.startTime_for_tictoc,1)), 'Elapsed: ', round(self.elapsed_time,2), 'Pause: ', round(self.pause_time,2), 'Phrase: ', round(self.phrase_time,2) )
            
        frames.append(data)
            
        if self.elapsed_time > settings.LISTEN_PHRASE_MIN_TIME: #reached min time
            if settings.LISTEN_PHRASETIMEOUT is not None and self.elapsed_time > settings.LISTEN_PHRASETIMEOUT: #reached max time
                print("MaxTimeLimit reached", self.elapsed_time) 
                frames.clear()               
                return "init"
            else:
                if self.pause_time > settings.LISTEN_PAUSE_THRESHOLD: #wait for pause at the end
                    if self.phrase_time > settings.LISTEN_PURE_PHRASE_TIME:
                        print("Pause ok and Phrase ok", self.pause_time, self.phrase_time)
                        return "recognition"
                    else:
                        print("Pause ok, Phrase not Ok", self.pause_time, self.phrase_time)    
                        return "init"    
                else:
                    return "phrase" # wait for more pause at the end of phrase
        else:
            return "phrase" #still waiting for min time           
        
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
    
    def state_recognition(self, frames):
        print("State-Recognition")
        frame_data = b"".join(frames)
        
        try:    
            import speech_recognition as sr #@UnusedImport #check if package is installed
        except:
            print("No speech_recognition installed on system. Try to use fallback...")
            import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
        
        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
        pluginEcho.echoStoreWav(audio)
            
              
        return "recognition"

    def start(self, detected_callback=None, interrupt_check=lambda: False, sleep_time=0.03):
        if interrupt_check is not None and interrupt_check():
            print("detect voice return")
            return        

        state = "init"
        frames = []
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
                state = self.state_phrase(data, frames, energy)
            elif state == "recognition":
                state = self.state_recognition(frames)
            else:
                print("Unknown state ", state)

        print("finished.")

    def terminate(self):       
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()


def run(model = "resources/lib/snowboyrpi8/", sensitivity=0.5, sleep = 0.03, interrupt_check = None, audio_gain = 1.0):    
    detector = HotwordDetector(model, sensitivity=sensitivity, audio_gain = audio_gain)
    print('Listening... ')    
    detector.start(detected_callback=None, interrupt_check=interrupt_check, sleep_time=sleep)
    detector.terminate()

if __name__ == '__main__': 
    run()
    