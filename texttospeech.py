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
        engine = pyttsx3.init()
        try:
            engine.setProperty('voice','german')
        except: 
            print("Could not set texttospeech language to german. Using default")
        engine.setProperty('volume', 1.0) 
        
        return engine
    else:
        return None
    
def sayString(engine, s):    
    if engine: 
        print(s)
        engine.say(s)
        engine.runAndWait()
    else:
        print("Warning: No audio output. ")
        print(s)
     
    