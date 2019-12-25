soundSupport = True
try:
    import pyttsx3    
except:
    soundSupport = False
#print(engine)
#voices = engine.getProperty('voices')
#for voice in voices:
#    engine.setProperty('voice', voice.id)
#    print(voice, voice.id)
#engine.say('Sally sells seashells by the seashore.')
    
def init():
    if soundSupport:
        return pyttsx3.init()
    else:
        return None
    
def sayString(engine, s):
    if engine: 
        engine.say(s)
        engine.runAndWait()
    else:
        print("Warning: No audio output. ")
        print(s)
     
    