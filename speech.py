# -*- coding: utf-8 -*-
import sys
import platform
import settings
import os
import audioop
import math
import collections 
import time
import pluginEcho

try:
    print(sys.version)
    print(platform.architecture())
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
     
try:    
    from resources.lib.snowboyrpi8 import snowboydecoder
except Exception as e:
    print("Warning: Could not import resources.lib.snowboyrpi8", str(e))     


#lobal varuables
interrupted = False
audio = None

def getAudioData():
    global audio
    return audio

def found_callback():
    global interrupted    
    interrupted = True
    print("Callback Found something. ", interrupted)


def check_callback():
    #print("Check callback")
    global interrupted    
    return interrupted


class MyRecognizer(sr.Recognizer): 
    
    
    def listen_mod(self, source, timeout=None, phrase_time_limit=None, snowboy_configuration=None):        
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.

        The ``timeout`` parameter is the maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.

        The ``phrase_time_limit`` parameter is the maximum number of seconds that this will allow a phrase to continue before stopping and returning the part of the phrase processed before the time limit was reached. The resulting audio will be the phrase cut off at the time limit. If ``phrase_timeout`` is ``None``, there will be no phrase time limit.

        The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).

        This operation will always complete within ``timeout + phrase_timeout`` seconds if both are numbers, either by returning the audio data, or by raising a ``speech_recognition.WaitTimeoutError`` exception.
        """
        assert isinstance(source, sr.AudioSource), "Source must be an audio source"
        assert source.stream is not None, "Audio source must be entered before listening, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"
        assert self.pause_threshold >= self.non_speaking_duration >= 0
        if snowboy_configuration is not None:
            assert os.path.isfile(os.path.join(snowboy_configuration[0], "snowboydetect.py")), "``snowboy_configuration[0]`` must be a Snowboy root directory containing ``snowboydetect.py``"
            for hot_word_file in snowboy_configuration[1]:
                assert os.path.isfile(hot_word_file), "``snowboy_configuration[1]`` must be a list of Snowboy hot word configuration files"

        seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
        #pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer))  # number of buffers of non-speaking audio during a phrase, before the phrase should be considered complete
        #phrase_buffer_count = int(math.ceil(self.phrase_threshold / seconds_per_buffer))  # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
        non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / seconds_per_buffer))  # maximum number of buffers of non-speaking audio to retain before and after a phrase

        print("MyListen: ")
        print("----------")
        print("pause_threshold: ", self.pause_threshold)
        print("phrase_threshold: ", self.phrase_threshold)        
        print("phrase_min_time: ", self.phrase_min_time)
        print("phrase_max_limit: ", phrase_time_limit)            
        print("----------")        
        #print("seconds_per_buffer: ", seconds_per_buffer)
        #print("pause_buffer_count: ", pause_buffer_count)
        #print("phrase_buffer_count: ", phrase_buffer_count)
        #print("non_speaking_buffer_count: ", non_speaking_buffer_count)
        #print("----------")
        # read audio input for phrases until there is a phrase that is long enough
        elapsed_time = 0  # number of seconds of audio read
        i = 0
        buffer = b""  # an empty buffer means that the stream has ended and there is no data left to read
        while True:
            print("energy_threshold: ", self.energy_threshold)
            frames = collections.deque()

            if snowboy_configuration is None:
                # store audio input until the phrase starts
                while True:
                    # handle waiting too long for phrase by raising an exception
                    elapsed_time += seconds_per_buffer
                    if timeout and elapsed_time > timeout:
                        raise sr.WaitTimeoutError("listening timed out while waiting for phrase to start")

                    buffer = source.stream.read(source.CHUNK)
                    if len(buffer) == 0: break  # reached end of the stream
                    frames.append(buffer)
                    if len(frames) > non_speaking_buffer_count:  # ensure we only keep the needed amount of non-speaking buffers
                        frames.popleft()

                    # detect whether speaking has started on audio input
                    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
                    if energy > self.energy_threshold: break

                    # dynamically adjust the energy threshold using asymmetric weighted average
                    if self.dynamic_energy_threshold:
                        damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
                        target_energy = energy * self.dynamic_energy_ratio
                        self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
            else:
                # read audio input until the hotword is said
                snowboy_location, snowboy_hot_word_files = snowboy_configuration
                buffer, delta_time = self.snowboy_wait_for_hot_word_mod(snowboy_location, snowboy_hot_word_files, source, timeout)
                elapsed_time += delta_time
                if len(buffer) == 0: break  # reached end of the stream
                frames.append(buffer)

            # read audio input until the phrase ends
            pause_count, phrase_count = 0, 0
            #phrase_start_time = elapsed_time
            print("Start second loop", len(buffer))
            
                  
            startTime_for_tictoc = time.time()        

            frames.clear()
            #phrase_start_time = 0
            elapsed_time = 0            
            phrase_time = 0.0     
            pause_time = 0.0       
            phrase_ok = False
            print("Seconds per buffer: ", seconds_per_buffer)
            while True:
                # handle phrase being too long by cutting off the audio
                elapsed_time += seconds_per_buffer                

                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0:
                    print("-------------------------REACHED END--------------------")
                    break  # reached end of the stream
                frames.append(buffer)
                phrase_count += 1

                # check if speaking has stopped for longer than the pause threshold on the audio input
                energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # unit energy of the audio signal within the buffer
                if energy > self.energy_threshold:
                    phrase_time += seconds_per_buffer
                    pause_count = 0
                else:
                    pause_count += 1
                    pause_time += seconds_per_buffer            
                i = i+1
                if i % 4 == 0:
                    print("Debugging: ", str(round(energy,2)), str(round(time.time() - startTime_for_tictoc,1)), 'Elapsed: ', round(elapsed_time,2), 'Pause: ', round(pause_time,2), 'Phrase: ', round(phrase_time,2) )
                
                if elapsed_time > self.phrase_min_time: #reached min time
                    if phrase_time_limit is not None and elapsed_time > phrase_time_limit: #reached max time
                        print("MaxTimeLimit reached", elapsed_time)
                        phrase_ok = False
                        break
                    else:
                        if pause_time > self.pause_threshold: #wait for pause at the end
                            if phrase_time > self.phrase_threshold:
                                phrase_ok = True
                                print("Pause ok and Phrase ok", pause_time, phrase_time)
                                break
                            else:
                                phrase_ok = False
                                print("Pause ok, Phrase not Ok", pause_time, phrase_time)    
                                return None    
                        else:
                            pass # wait for more pause at the end of phrase
                else:
                    pass #still waiting for min time                
 

            print("Ended second loop", len(buffer))
            # check how long the detected phrase is, and retry listening if the phrase is too short
            phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
            #if phrase_count >= phrase_buffer_count or len(buffer) == 0:
            if phrase_ok:
                print("Reached end of phrase", len(buffer))
                break  # phrase is long enough or we've reached the end of the stream, so stop listening
            else: 
                print("Expression was too short. Starting all over again")

        # obtain frame data
        for _ in range(pause_count - non_speaking_buffer_count): frames.pop()  # remove extra non-speaking frames at the end
        frame_data = b"".join(frames)

        print("Collected all data. Finished listening", len(buffer))
        return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
    

    def snowboy_wait_for_hot_word_mod(self, snowboy_location, snowboy_hot_word_files, source, timeout=None):
        # load snowboy library (NOT THREAD SAFE)
        sys.path.append(snowboy_location)

        sys.path.pop()
        
        print("My Snowboy Wait")   
        global interrupted
        
        interrupted = False
        
        model = snowboy_hot_word_files

        detector = snowboydecoder.HotwordDetector(model, sensitivity=0.9)
        print('Listening... Press Ctrl+C to exit')

        # main loop
        detector.start(detected_callback=found_callback, interrupt_check=check_callback, sleep_time=0.03)

        detector.terminate()
        print("Terminate my snowboy wait, returning empty string and zero...")
        
        seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
        elapsed_time = seconds_per_buffer
        buffer = source.stream.read(source.CHUNK)
        
        #elapsed_time = 1
        print(elapsed_time)
        print("---------------Buffer-----------------")
        #print(buffer)
        
        return b"".join(buffer), elapsed_time   #add dummy buffer



def speechListen(recognizer, microphone):   
    # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    print(microphone.SAMPLE_RATE)
    print(microphone.SAMPLE_WIDTH)
    global audio
    while audio is None:
        with microphone as source:
            print("Adjusting silence...")
            recognizer.energy_threshold = settings.LISTEN_ENERGY_THRESHOLD #reset dynamic limit
            recognizer.adjust_for_ambient_noise(source, duration = 1)
                            
            try:           
                if settings.hasSnowboy():
                    print("Listening with snowboy")
                    audio = recognizer.listen_mod(source, timeout=settings.LISTEN_TIMEOUT, phrase_time_limit=settings.LISTEN_PHRASETIMEOUT, snowboy_configuration=settings.LISTEN_SNOWBOY )
                else:
                    print("Listening WITHOUT snowboy")
                    audio = recognizer.listen_mod(source, timeout=settings.LISTEN_TIMEOUT, phrase_time_limit=settings.LISTEN_PHRASETIMEOUT )
                    
            except Exception as e:
                print("Listening failed: ", str(e))
                #audio = recognizer.listen(source, timeout=settings.LISTEN_TIMEOUT, phrase_time_limit=settings.LISTEN_PHRASETIMEOUT, snowboy_configuration=None   ) 
    
    print("Stopped listening")
    #pluginEcho.echoEcho()
    #print("exit")
    #sys.exit()
    # set up the response object
    response = {"error": None, "transcription": None }
    
    try:
        if settings.LISTEN_LANGUAGE == "":
            settings.LISTEN_LANGUAGE = None
        
        print("Starting speech recognition...")
            
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
        
    print("Speech recognition finished")

    return response

def speechInit():
    # create recognizer and mic instances
    recognizer = MyRecognizer()#sr.Recognizer()

    for mic in enumerate(sr.Microphone.list_microphone_names()):
        print(mic)
        
    recognizer.phrase_threshold = settings.LISTEN_PURE_PHRASE_TIME    
    recognizer.pause_threshold = settings.LISTEN_PAUSE_THRESHOLD    
    recognizer.phrase_min_time = settings.LISTEN_PHRASE_MIN_TIME  
    
    microphone = sr.Microphone(device_index = settings.LISTEN_MIC_INDEX, sample_rate=settings.LISTEN_SAMPLERATE, chunk_size=settings.LISTEN_CHUNKSIZE)
    
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer) and not isinstance(recognizer, MyRecognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    return (recognizer, microphone)