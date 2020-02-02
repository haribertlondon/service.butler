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
# sudo apt-get install gpiozero
# pip install pyttsx3
# pip install playsound
# pip install SpeechRecognition
#   set kodi as autostart: 
#		?????, i did it with sudo apt-get install cron; cron -e; add line-> @reboot sleep 10; kodi --standalone
# install this package with zip file

import sys, traceback
import ai
import settings
import texttospeech 
import stateMachine
import gpio
         
def detected_callback(response): #audio):
    try:
        validCommand = False
        result = ai.speechInterprete(response)
                
        print('Result=', result)
        
        #check result
        try:
            if result is not None and isinstance(result, dict): 
                if 'result' in result and result['result']:
                    validCommand = True
                else:
                    raise Exception("Command was not successful")
            
                if 'message' in result:
                    if result['message'] == 'Silence!' or result['message'] == 'OK':
                        print(result) #if everything is ok, no output
                    else:
                        texttospeech.sayString(result['message']) 
                else:
                    raise Exception("No message text found")
            else:
                raise Exception("Result is not dictionary")
        except Exception as e:
            print("Command not executed. ",  e, result)
    
    except Exception as e:
        print("Fatal error in ai.callback: ", e)
        traceback.print_exc(file=sys.stdout)
        
    return validCommand
        
        
def listening_callback():
    #pluginKodi.kodiShowMessage("Listening...")
    print("Listening....")

if __name__ == "__main__":    
    gpio.init()
    detector = stateMachine.HotwordDetectorStateMachine(decoder_model = settings.LISTEN_SNOWBOY_MODELS, sensitivity=settings.LISTEN_SNOWBOY_SENSITIVITY, audio_gain = settings.LISTEN_AUDIO_GAIN)    
    detector.start(detected_callback=detected_callback, listening_callback = listening_callback)
    detector.terminate()
    
    sys.exit()
