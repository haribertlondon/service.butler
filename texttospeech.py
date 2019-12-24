import pyttsx3
#print(engine)
#voices = engine.getProperty('voices')
#for voice in voices:
#    engine.setProperty('voice', voice.id)
#    print(voice, voice.id)
#engine.say('Sally sells seashells by the seashore.')
    
def init():
    return pyttsx3.init()
    
def sayString(engine, s):
    engine.say(s)
    engine.runAndWait()
     
    