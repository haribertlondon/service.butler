# -*- coding: utf-8 -*-

#what is needed for raspberry:
# install raspbian
#   sudo apt-get install lxde  
# 	set autologin 
#   	#sudo raspi-config
#   	  
# 	config screen with 
#		#sudo nano /boot/config.txt 
#   set fixed IP address with .... or at router
#   
#   
# sudo apt-get install kodi
# sudo apt-get install kodi-vfs-sftp
# sudo apt-get install flac
# sudo apt-get install python-pyaudio
# sudo apt-get install python-pip
# sudo apt-get install libespeak-dev
# pip install pyttsx3
# pip install SpeechRecognition
#   set kodi as autostart: 
#		?????, i did it with sudo apt-get install cron; cron -e; add line-> @reboot sleep 10; kodi --standalone
# install this package with zip file

import speech
import sys
#import settings
import ai
import settings
import texttospeech 
import speech2     
         
         
def detected_callback(response, audio):
    result = ai.speechInterprete(response)
                
    print('Result=', result)
    if result and isinstance(result, dict) and 'message' in result:
        if result['message'] != 'Silence!':
            texttospeech.sayString(textspeech, result['message'])
        else: 
            #silence
            print(result['message'])
    else:
        texttospeech.sayString(textspeech, 'Sum Sum Sum')

if __name__ == "__main__":    
    (recognizer, microphone) = speech.speechInit()
    textspeech = texttospeech.init()
    
    speech2.run(sensitivity=0.5, sleep = 0.03, detected_callback = detected_callback, audio_gain = 1.0)
    sys.exit()

#    while True:
#        
#        if not settings.isDebug() or True:
#            guess = speech.speechListen(recognizer, microphone)
#        else: 
#            #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele Modern Family weiter" }    
#            #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele letzte Serie weiter" }
#            #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele MacGyver weiter" }
#            #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele die letzte Tagesschau" }
#            #guess =  {"error": None, "transcription": "KODi weiter" }
#            #guess =  {"error": None, "transcription": "Kodi Starte die letzten Tagesthemen" }
#            #guess =  {"error": None, "transcription": "Kodi Youtube mit Trailer Deutsch" }
#            #guess =  {"error": None, "transcription": "Kodi Echo Hallo Kristina" }
#            guess =  {"error": None, "transcription": "Kodi Spiele SWR3" }
#            
#        
#        print(guess)
#        result = ai.speechInterprete(guess)
#                
#        print('Result=', result)
#        if result and isinstance(result, dict) and 'message' in result:
#            if result['message'] != 'Silence!':
#                texttospeech.sayString(textspeech, result['message'])
#        else:
#            texttospeech.sayString(textspeech, 'Sum Sum Sum')
#            
#        
#    print("Script finished")
