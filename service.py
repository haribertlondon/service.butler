import json
import urllib
import difflib
import speech_recognition as sr

KEYWORD = "kodi"
LISTEN_CHUNKSIZE = 1024
LISTEN_SAMPLERATE = None 
LISTEN_MIC_INDEX = None
LISTEN_TIMEOUT = None
LISTEN_PHRASETIMEOUT = 10
LISTEN_LANGUAGE= 'de-DE' #["en-US",'de']
LISTEN_GOOGLEKEY = None
HTTP_TIMEOUT = 20
#Todo
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
    microphone = sr.Microphone(device_index = LISTEN_MIC_INDEX, sample_rate=LISTEN_SAMPLERATE, chunk_size=LISTEN_CHUNKSIZE)
    
    
    for mic in enumerate(sr.Microphone.list_microphone_names()):
        print(mic) 
    
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    return (recognizer, microphone)
  
  
def getUrl(command, typeStr, searchStr):    
    hostname = 'http://192.168.0.40:8080/jsonrpc'
    url = hostname
    post = None
    if command == "search": 
        if typeStr == "movies":
            post = b'{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str.encode(searchStr)+b'"}, "properties" : ["dateadded", "lastplayed", "year", "rating", "playcount", "genre"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows":
            post = b'{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str.encode(searchStr)+b'"}, "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play" or command == "pause":
        post = b'{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1 },"id":1}'        
    elif command == "open":
        post = b'{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"movieid": '+str.encode(str(searchStr))+ b'} }, "id": 1 }' #geht!!!
            
    return (url, post)
   
def downloadBinary(url, post): 
    print(url, post)  
    try:
        req = urllib.request.Request(url)        
        #req.add_header('User-Agent', '')
        req.add_header('Content-Type','application/json')
        r = urllib.request.urlopen(req, data = post, timeout=HTTP_TIMEOUT)#, headers = {'content-type': 'application/json'})
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
    
    command = command.replace(KEYWORD.lower(),"", 1).strip()
    
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
        #guess =  {"error": None, "transcription": KEYWORD + " " + "play the beach" }    
        print(guess)
        speechInterprete(guess)
        
    print("Script finished")