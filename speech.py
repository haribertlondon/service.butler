# -*- coding: utf-8 -*-
import collections
import pyaudio
import math
import pluginEcho
import mysphinx
import settings
import audioop
import time

try:    
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
try:
    from resources.lib.snowboyrpi8 import snowboydetect as snowboydetect #@UnresolvedImport
except Exception as e:
    print("Could not load snowboy detect", e)        
  
def getByteArray(lst):    
    flat_list = [item for sublist in lst for item in sublist]    
    if settings.isPython3():
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
        self.pythonaudio = pyaudio.PyAudio()
        self.frames = []
        self.infos = []        
        
        self.sphinxrecognizer = mysphinx.MyRecognizer() #sr.Recognizer()  
        try:
            self.sphinxrecognizer.prepare_sphinx2(language = "en-GIT", keyword_entries = settings.LISTEN_SPHINX_KEYWORDS) 
        except:
            pass

        for mic in enumerate(sr.Microphone.list_microphone_names()):
            print(mic)  
        
        default_info = self.pythonaudio.get_default_input_device_info()
        print("Default microphone info ", default_info)
        
        if settings.LISTEN_MIC_INDEX is None:
            settings.LISTEN_MIC_INDEX = default_info['index']            
        
        self.sample_width = pyaudio.get_sample_size(self.audio_format)
        self.energy_threshold = settings.LISTEN_ENERGY_THRESHOLD 
        self.stream_in = self.pythonaudio.open( input=True,  output=False, input_device_index=settings.LISTEN_MIC_INDEX, format= self.audio_format, channels=self.num_channels, rate=self.sample_rate, frames_per_buffer=self.chunksize, stream_callback=audio_callback)
        
    def hotword_snowboy(self):
        try:
            frame_data = getByteArray(self.frames)
            result = self.detector.RunDetection(frame_data)
        except Exception as e:
            print("Snowboy Exception. Reason ", e)
            result = 0
        return result
        
    def hotword_sphinx(self):
        try:       
            frame_data = getByteArray(self.frames)
            audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
            a = self.sphinxrecognizer.recognize_sphinx2(audio_data = audio, onlykeywords = True)                    
        except Exception as e:                        
            print("Sphinx Exception. Reason ", e)
            a = ""          
        
        if len(a)>0:
            print("Detected the word: " + a)
            return 1
        else:
            return 0
        
    def resetFrameBuffer(self):
        self.frames[:] = []
        self.infos[:] = []
        
        
    def applyLowPassFilter(self, energy, tau):        
        damping = math.exp( - self.cycleTime / tau ) #mit damping=exp(-0.023/tau) self.seconds_per_buffer = 0.023 
        target_energy = energy * settings.LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_RATIO
        self.energy_threshold = self.energy_threshold * damping + target_energy * (1.0 - damping) #y(n) = damping*y(n-1) + (1-damping)*x(n)
        
    def storeWav(self):
        frame_data = getByteArray(self.frames)
        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
        pluginEcho.echoStoreWav(audio) 
        
    def recognize(self):
        frame_data = getByteArray(self.frames)
        audio = sr.AudioData(frame_data, self.sample_rate, self.sample_width)
            
        recognizer = sr.Recognizer()
        response = {"error": None, "transcription": None }
        try:    
            response["transcription"] = recognizer.recognize_google(audio, key=None, language=settings.LISTEN_LANGUAGE)
        except sr.RequestError as e:
            response["error"] = "API unavailable " +  str(e) # API was unreachable or unresponsive
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech" # speech was unintelligible
            
        if settings.isDebug():# or True:    
            pluginEcho.echoStoreWav(audio) 
            
        return response 
    
    def cutLeftFramesToMaxBufferSize(self, maxFrameLenSeconds):
        #ringbuffer: Cut old frames if buffer is too long
        if maxFrameLenSeconds<=0:
            self.frames[:] =[]
            self.infos[:] = []
        else:
            newLength = (int)(maxFrameLenSeconds / self.seconds_per_buffer)
            if newLength < len(self.frames): 
                self.frames = self.frames[-newLength:]   
                self.infos = self.infos[-newLength:]                

    def cutRightFrames(self, cutSeconds):
        #ringbuffer: Cut old frames if buffer is too long
        bufferLenOfPause = (int)( cutSeconds / self.seconds_per_buffer) 
        if bufferLenOfPause> 0 and bufferLenOfPause < len(self.frames):
            self.frames = self.frames[:-bufferLenOfPause]
            self.infos = self.infos[:-bufferLenOfPause]
    
    def updateFrames(self, maxFrameLenSeconds):
        
        #get data from other thread            
        chunk = self.ring_buffer.get()
        if len(chunk) == 0:                
            return (0, 0)
        
        chunkSize = len(chunk)
        
        #analyze one chunk
        dataArray = getByteArray(chunk)
        energy = audioop.rms(dataArray, self.sample_width)
        isEnergy = energy > self.energy_threshold
        isHotWord = False 
       
        #whole frame buffer
        self.frames.extend(chunk)        
        self.infos.append( (isEnergy, isHotWord) )                  
        
        self.cutLeftFramesToMaxBufferSize(maxFrameLenSeconds)
              
        return (energy, chunkSize)

    def terminate(self):       
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.pythonaudio.terminate()

