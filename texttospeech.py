# -*- coding: utf-8 -*-
#soundSupport = True
#try:
#    import pyttsx3    
#except:
#    soundSupport = False
#print(engine)
#voices = engine.getProperty('voices')
#for voice in voices:
#    engine.setProperty('voice', voice.id)
#    print(voice, voice.id)
#engine.say('Sally sells seashells by the seashore.')
    
import os
from gtts import gTTS
import settings
from google_speech import Speech
import playsound

    
if settings.isPython3():
    from urllib.parse import quote  # Python 3+    
else:
    from urllib import quote  # Python 2.X @UnresolvedImport

def init():
    try:
        import pyttsx3
        engine = pyttsx3.init()
        try:
            print("Set language to german")
            #engine.setProperty('voice','german')
        except: 
            print("Could not set texttospeech language to german. Using default")
        engine.setProperty('volume', 1.0) 
        
        return engine
    except Exception as e:
        print("Cannot activate texttospeech",e)
        return None
    print("init text to speech")
    
def sayStringX(engine , text):
    try:
        sayStringPack(engine, text)
    except Exception as e:
        print(e)
        sayString_old(engine, text)

def sayStringPack(_ , text):    
    speech = Speech(text, "de")
    speech.play()

def sayString(_,text):
    tts = gTTS(text, lang='de')
    tts.save('response.mp3')
    playsound.playsound('response.mp3', True)
    
    
def sayString_old(engine, s):
    #s="Hallo "+s
    print("Voice output", s)
    try:          
        cleanStr = quote(str(s))        
        print("Output by google", cleanStr)
                
        a = os.system('/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q='+str(cleanStr)+'&tl=de";')
        if a is not 0:
            raise Exception("No output with google possible")
        
    except Exception as e:
        print("Error during google output. Try fallback. Reason was ", str(e))
        if engine:
            engine.say(s)
            engine.runAndWait()
        else:
            print("Warning: No audio output. ")
     
    

if __name__ == "__main__":
    engine = init()
    #sayString(engine,"I want to have cup cakes. I want to have vacations")
    sayString(engine,u"Ich will eine eiskalte Hündin haben")
    print("Finished")

