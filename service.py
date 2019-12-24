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




import platform
import sys
print(sys.version)
print(platform.architecture())

if (sys.version_info > (3, 0)):
    import urllib.request as urlrequest
else:
    import urllib2 as urlrequest

import json
import difflib
#import resources.lib.speech_recognition as sr
import speech_recognition as sr


HOTWORD = "kodi"
LISTEN_CHUNKSIZE = 1024
LISTEN_SAMPLERATE = None 
LISTEN_MIC_INDEX = None
LISTEN_TIMEOUT = None
LISTEN_PHRASETIMEOUT = 10
LISTEN_LANGUAGE= 'de-DE' #["en-US",'de']
LISTEN_GOOGLEKEY = None
HTTP_TIMEOUT = 20
#Todo
#make script to run on Kodi or on Linux
#Grammatik systematisch
#mehrere keywords fuer kodi, tannenbaum, chefkoch
#tagesschau aktivieren
#sprachausgabe
#dateien auslagern
#plugins ermoeglichen
#mixed language support
#parametetrisieren im header
#am Raspberry testen
#listen Befehl: The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).




def speechListen(recognizer, microphone):   
    # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        print("Adjust silence")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening")
        audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=LISTEN_PHRASETIMEOUT)

    print("Stopped listening")
    # set up the response object
    response = {"error": None, "transcription": None }
    
    try:
        response["transcription"] = recognizer.recognize_google(audio, key=LISTEN_GOOGLEKEY, language=LISTEN_LANGUAGE)
    except sr.RequestError:
        # API was unreachable or unresponsive        
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

def speechInit():
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    
    for mic in enumerate(sr.Microphone.list_microphone_names()):
        print(mic) 
    
    microphone = sr.Microphone(device_index = LISTEN_MIC_INDEX, sample_rate=LISTEN_SAMPLERATE, chunk_size=LISTEN_CHUNKSIZE)
    
    

    
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    return (recognizer, microphone)
  
  
def getUrl(command, typeStr, searchStr):    
    hostname = 'http://192.168.0.161:8080/jsonrpc'
    url = hostname	
    post = None
    if command == "search": 
        if typeStr == "movies":
            post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties" : ["dateadded", "lastplayed", "year", "rating", "playcount", "genre"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows":
            post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play" or command == "pause":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1 },"id":1}'        
    elif command == "open":
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"movieid": '+str(searchStr)+ '} }, "id": 1 }' #geht!!!
     
    post = str.encode(post)
    return (url, post)
   
def downloadBinary(url, post): 
    print(url, post)  
    try:
        req = urlrequest.Request(url)        
        #req.add_header('User-Agent', '')
        req.add_header('Content-Type','application/json')
        r = urlrequest.urlopen(req, data = post, timeout=HTTP_TIMEOUT)#, headers = {'content-type': 'application/json'})
        html = r.read()
    except Exception as e:
        print(("Error with link "+str(url) + ' Exception: ' + str(e)))        
        html = "" 
        
    return html

def getPlayableItems(typeStr, searchStr):
    (url, post) = getUrl("search", typeStr, searchStr)
    html = downloadBinary(url, post)  
    print(html)
    js = json.loads(html)
    try:
        items = js['result'][typeStr]
    except:
        print("Wrong json response: "+str(js))
        items = []
    return items

def getBestMatch(searchStr, dic):
    try:          
        bestids = difflib.get_close_matches(searchStr, [item['label'] for item in dic])
        print(bestids)
        best = [item for item in dic if bestids[0]==item['label']]
        print(best)
        return best[0]
    except:
        return []   

# Examples Play The Beach
def speechInterprete(guess):
    
    if guess["error"] is not None or guess["error"] is not None and len(guess["error"])>0:
        print("Guessed expression not valid "+str(guess))
        return 
    
    command = guess["transcription"].lower()
    
    command = command.replace(HOTWORD.lower(),"", 1).strip()
    
    if command == "play" or command == "pause":
        (url, post) = getUrl("play", None, None)
        print(url)
        html = downloadBinary(url, post)
        print(html)
    elif "spiel" in command or "spiele" in command or "play" in command:
        # search best match
        command = command.replace("play","",1).strip() 
        command = command.replace("spiele","",1).strip()       
        command = command.replace("spiel","",1).strip()
        items = getPlayableItems("movies", command)
        item = getBestMatch(command, items)        
        #play
        if len(item)>0:  
            (url, post) = getUrl("open", None, item["movieid"])        
            html = downloadBinary(url, post)        
          
        

if __name__ == "__main__":    
    (recognizer, microphone) = speechInit()  
    
    for i in range(100):
        
        guess = speechListen(recognizer, microphone) 
        #guess =  {"error": None, "transcription": HOTWORD + " " + "play the beach" }    
        print(guess)
        speechInterprete(guess)
        
    print("Script finished")
