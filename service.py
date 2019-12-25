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
# pip install SpeechRecognition
#   set kodi as autostart: 
#		?????, i did it with sudo apt-get install cron; cron -e; add line-> @reboot sleep 10; kodi --standalone
# install this package with zip file

import speech
import settings
import ai
import texttospeech

#------TODO-------
#durchstich
#letzte tvshow weiterspielen
#tagesschau aktivieren

#youtube support
#echo Befehl implementieren zum Test der Klangqualität
#Ringpuffer für Aufnahmen
#mehrere keywords fuer kodi, tannenbaum, chefkoch
#plugins ermoeglichen
#listen Befehl: The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).

#--------DONE---------------
#Grammatik systematisch
#parametetrisieren im header
#sprachausgabe
#make script to run on Kodi !!OR!! on Linux
#am Raspberry testen
#mixed language support
#dateien auslagern

          
         

if __name__ == "__main__":    
    (recognizer, microphone) = speech.speechInit()
    textspeech = texttospeech.init()

    
    for i in range(100):
        #guess = speech.speechListen(recognizer, microphone) 
        #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele Modern Family weiter" }    
        #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele letzte Serie weiter" }
        guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele MacGyver weiter" }
        print(guess)
        result = ai.speechInterprete(guess, None)
        
        #if not result['result']:
        print('Voice output: ', result['message'])
        if result and isinstance(result, dict) and 'message' in result and False:
            texttospeech.sayString(textspeech, result['message'])
        else:
            texttospeech.sayString(textspeech, 'Sum Sum Sum')
            
        break
        
    print("Script finished")
