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
# sudo apt-get install python-audioop
# sudo apt-get install python-git
# sudo apt-get install python-pyttsx3
# sudo apt-get install python-pocketsphinx
# pip install pyttsx3
# pip install playsound
# pip install SpeechRecognition
#   set kodi as autostart: 
#		?????, i did it with sudo apt-get install cron; cron -e; add line-> @reboot sleep 10; kodi --standalone
# install this package with zip file

import sys
import ai
import settings
import texttospeech 
import speech
import pluginKodi
         
         
def detected_callback(response, _): #audio):
    try:
        result = ai.speechInterprete(response)
                
        print('Result=', result)
        if result and isinstance(result, dict) and 'message' in result:
            if result['message'] != 'Silence!' and result['message'] != 'OK':
                texttospeech.sayString(textspeech, result['message'])
            else: 
                #silence
                print(result['message'])
        else:
            texttospeech.sayString(textspeech, 'Sum Sum Sum')
    
    except Exception as e:
        print("Fatal error in ai.callback: ", e)
        
def listening_callback():
    #pluginKodi.kodiShowMessage("Listening...")
    print("Listening....")

if __name__ == "__main__":
    textspeech = texttospeech.init()
    
    speech.run(sensitivity=settings.LISTEN_SNOWBOY_SENSITIVITY, detected_callback = detected_callback, audio_gain = settings.LISTEN_AUDIO_GAIN, listening_callback=listening_callback)
    sys.exit()
