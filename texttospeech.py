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
    
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

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
    
def sayString(engine, s):
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
    sayString(engine,"I want to have cup cakes. I want to have vacations")
    sayString(engine,"Ich will cup cakes")

