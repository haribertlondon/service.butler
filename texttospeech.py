# -*- coding: utf-8 -*-

from gtts import gTTS
#import playsound
import pluginEcho

tempFileName = 'response.mp3'
      
def generateMp3(text, tempFileName):
    tts = gTTS(text, lang='de')
    tts.save(tempFileName)
 
def playMp3(tempFileName):
    #playsound.playsound(tempFileName)
    pluginEcho.echoPlay(tempFileName)      

def sayString(text):
    generateMp3(text, tempFileName)
    playMp3(tempFileName)   
    

if __name__ == "__main__":    
    #sayString(engine,"I want to have cup cakes. I want to have vacations")
    sayString(u"Ich will eine eiskalte Hündin haben")
    #playMp3(tempFileName)
    print("Finished")

