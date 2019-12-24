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
import pluginKodi
import settings

#Todo
#Grammatik systematisch
#mehrere keywords fuer kodi, tannenbaum, chefkoch
#tagesschau aktivieren
#sprachausgabe
#plugins ermoeglichen
#parametetrisieren im header
#listen Befehl: The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).

#--------DONE---------------
#make script to run on Kodi !!OR!! on Linux
#am Raspberry testen
#mixed language support
#dateien auslagern



# Examples Play The Beach
def speechInterprete(guess):
    
    if guess["error"] is not None or guess["error"] is not None and len(guess["error"])>0:
        print("Guessed expression not valid "+str(guess))
        return 
    
    command = guess["transcription"].lower()
    
    command = command.replace(settings.LISTEN_HOTWORD.lower(),"", 1).strip()
    
    if command == "play" or command == "pause":
        pluginKodi.kodiPlayPause()
    elif "spiel" in command or "spiele" in command or "play" in command:
        # search best match
        movieTitle = command
        movieTitle = movieTitle.replace("play","",1).strip() 
        movieTitle = movieTitle.replace("spiele","",1).strip()       
        movieTitle = movieTitle.replace("spiel","",1).strip()
        pluginKodi.kodiOpenMovie(movieTitle)
          
         

if __name__ == "__main__":    
    (recognizer, microphone) = speech.speechInit()  
    
    for i in range(100):        
        guess = speech.speechListen(recognizer, microphone) 
        #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "play the beach" }    
        print(guess)
        speechInterprete(guess)
        break
        
    print("Script finished")
