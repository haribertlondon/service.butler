# -*- coding: utf-8 -*-
import sys
import platform
import settings

try:
    print(sys.version)
    print(platform.architecture())
    import speech_recognition as sr #@UnusedImport #check if package is installed
except:
    print("No speech_recognition installed on system. Try to use fallback...")
    import resources.lib.speech_recognition as sr #@Reimport #if not, use the provides ones
  

def speechListen(recognizer, microphone):   
    # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        print("Adjust silence")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening")
        audio = recognizer.listen(source, timeout=settings.LISTEN_TIMEOUT, phrase_time_limit=settings.LISTEN_PHRASETIMEOUT)
    
    print("Stopped listening")
    
    if settings.LISTEN_WRITEWAV is not None and len(settings.LISTEN_WRITEWAV)>0:
        wavdata = audio.get_wav_data()
        f = open(settings.LISTEN_WRITEWAV, 'wb')
        f.write(wavdata)
        f.close()
    
    # set up the response object
    response = {"error": None, "transcription": None }
    
    try:
        if settings.LISTEN_LANGUAGE == "":
            settings.LISTEN_LANGUAGE = None
            
        response["transcription"] = recognizer.recognize_google(audio, key=None, language=settings.LISTEN_LANGUAGE)
        #response["transcription"] = recognizer.recognize_wit(audio, key='6PKAY4NP4U4VJPBJAEHSWV7JS5HWTSQE')
        #response["transcription"] = recognizer.recognize_wit(audio, key='6PKAY4NP4U4VJPBJAEHSWV7JS5HWTSQE')
        #response["transcription"] = recognizer.recognize_bing(audio, key='912b8cb579f74a01aba54691b1d9c671')#, language=settings.LISTEN_LANGUAGE)
        #response["transcription"] = recognizer.recognize_sphinx(audio, language='en-US')#settings.LISTEN_LANGUAGE)#, language=settings.LISTEN_LANGUAGE)
        
        
        
    except sr.RequestError:
        # API was unreachable or unresponsive        
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

def speechInit():
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    
    for mic in enumerate(sr.Microphone.list_microphone_names()):
        print(mic) 
    
    microphone = sr.Microphone(device_index = settings.LISTEN_MIC_INDEX, sample_rate=settings.LISTEN_SAMPLERATE, chunk_size=settings.LISTEN_CHUNKSIZE)
    
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    return (recognizer, microphone)