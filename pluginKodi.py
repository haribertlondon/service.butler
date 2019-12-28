# -*- coding: utf-8 -*-
import difflib 
import htmlrequests
import settings

def getKodiUrl(command, typeStr, searchStr):    
    hostname = 'http://' + settings.HTTP_KODI_IP + '/jsonrpc'
    url = hostname    
    post = None
    if command == "search": 
        if typeStr == "movies" or typeStr == "movie":
            post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties" : ["dateadded", "lastplayed", "year", "rating", "playcount", "genre"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows":
            post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {                                                                                      "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1, "play":true },"id":1}'        
    elif command == "pause":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1 ,"play":false},"id":1}'
    elif command == "open":
        if typeStr == 'movies' or typeStr == 'movie': 
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"movieid": '+str(searchStr)+ '} }, "id": 1 }'
        elif typeStr == 'tvshows' or typeStr == 'episodes' or typeStr == 'episode': 
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"episodeid": '+str(searchStr)+ '} }, "id": 1 }'
        else:
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"playlistid": ' +str(searchStr) + '} }, "id": 1 }'
                                                                
    elif command == 'info':
        post = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "season", "episode", "showtitle", "rating"], "playerid": 1 }, "id": "VideoGetItem"}'
    elif command == 'stop':
        post = '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid": 1 },"id":1}'
    elif command == 'lastepisode':         
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes", "params": { "tvshowid": '+str(searchStr)+', "properties": ["title", "rating", "season"],  "limits": { "start" : 0, "end": 10 },   "filter": {"and": [{"field": "playcount", "operator": "is", "value": "0"}, {"field": "season", "operator": "greaterthan", "value": "0"}]},    "sort": { "order": "ascending", "method": "episode" } }, "id": "libEpisodes"}'        
    elif command == 'lasttvshow':            
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {  "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "descending", "method": "lastplayed" } }, "id": "libTvshows"}'    
    elif command == 'tagesschau':                   
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"file": "plugin://plugin.video.tagesschau/?action=play_video&feed=latest_broadcasts&tsid='+searchStr+'"  } }, "id": 1 }'
    elif command == 'youtube':
        post = '{"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"plugin://plugin.video.youtube/play/?video_id='+searchStr+'"}},"id":"1"}'    
    #elif command == 'tagesschau':                   
    #    post = '{ "jsonrpc": "2.0", "method": "Addons.ExecuteAddon","params":{"addonid":"plugin.video.tagesschau","params":{"action":"list_feed","feed":"latest_broadcasts" }}, "id": 1 }'
    #elif command == 'getplaylist':
    #    post = '{"jsonrpc": "2.0", "method": "Playlist.GetItems", "params": { "properties": [ "runtime", "showtitle", "season", "title", "artist", "file" ], "playlistid": 1}, "id": 1}'           
       
    post = str.encode(post) # set to byte array
    return (url, post)

def getPlayableItems(typeStr, searchStr):
    (url, post) = getKodiUrl("search", typeStr, searchStr)
    js = htmlrequests.downloadJsonDic(url, post)
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
    
def postKodiRequest_Internal(url, post):
    result = htmlrequests.htmlPostRequest(url, post)
    if result['result']: 
        return result
    else:   
        return { 'result': False,  'message' : 'Fehlgeschlagen. Grund: ' + getErrorMessage(result) }
    
def postKodiRequest(command, typeStr, searchStr):
    (url, post) = getKodiUrl(command, typeStr, searchStr) 
    return postKodiRequest_Internal(url, post)
    
def kodiPlay():
    return postKodiRequest("play", None, None)   

def kodiPause():    
    return postKodiRequest("pause", None, None)  

def kodiStop():  
    return postKodiRequest("stop", None, None) 

def getLastEpisode(tvshowid):        
    return postKodiRequest("lastepisode", None, tvshowid)

def kodiGetCurrentPlaying():
    #(url, post) = getKodiUrl("info", None, None)
    result = postKodiRequest("info", None, None)
    info = 'Spiele gerade ' + result['data']['item']['title'] 
    try:
        info = info + ' mit ' + str(round(result['data']['item']['rating'],1)).replace(".",",") + ' Sternen'
    except:
        pass
    try:
        info = info + ' aus ' + str(result['data']['item']['showtitle']) + ' in Staffel ' + str(result['data']['item']['season']) + ' Episode ' + str(result['data']['item']['episode'])  
    except:
        pass
    return { 'result': False,  'message' : info}

def kodiPlayTVShowLastEpisodeByName(tvShowTitle):  
    items = getPlayableItems("tvshows", tvShowTitle)
    item = getBestMatch(tvShowTitle, items)        
        
    #play item
    if len(item)>0 and "tvshowid" in item :
        return kodiPlayTVShowLastEpisodeById(item['tvshowid'])
    else:
        return { 'result': False,  'message' : "Keinen Film mit Namen " + str(tvShowTitle) +  " gefunden"}   
 
def kodiPlayEpisode(episodeId):    
    return postKodiRequest('open', 'episode', episodeId)      
    
def kodiPlayTVShowLastEpisodeById(tvshowid):    
      
    result = getLastEpisode(tvshowid)
    
    if 'result' in result and result['result'] and 'data' in result and len(result['data']['episodes'])>0: 
        #result = { 'result': True,  'message' : "Starte " + str(result["data"])}
        return kodiPlayEpisode(result['data']['episodes'][0]['episodeid'])
    else:   
        result = { 'result': False,  'message' : result['message'] + ' Keine Episode dieser Serie gefunden, die abgespielt werden kann. Grund: ' +getErrorMessage(result)  }        
    
    return result

def kodiPlayLastTvShow():            
    result = postKodiRequest("lasttvshow", None, None)
    if 'result' not in result or not result['result'] or 'data' not in result or 'tvshows' not in result['data'] or len(result['data']['tvshows'])==0:
        return result
    else:
        tvshowid = result['data']['tvshows'][0]['tvshowid']
        return kodiPlayTVShowLastEpisodeById(tvshowid)    
 
def kodiPlayYoutube(searchStr):    
    searchStr = searchStr.replace(" ","+")
    try:
        url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=30&order=relevance&q='+searchStr+'&key=AIzaSyDCgSFYMKR4IJsIM-BkZXMuqaVHkqRjXzI'
        js = htmlrequests.downloadJsonDic(url,None)
        videoId = js['items'][0]['id']['videoId']
        result = postKodiRequest("youtube", None, videoId)
    except Exception as e:
        result = {'result': False, 'message' : 'Youtube kann nicht gestartet werden '+str(e)}
    print(js)
    return result
 
def kodiPlayTagesschau(showStr):
    try:
        js = htmlrequests.downloadJsonDic('http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json',b'')    
        print(js)
        ts = [x for x in js['latestBroadcastsPerType'] if x['title']==showStr][0]['sophoraId'] 
        print(ts)
        try:
            strts = ts.encode('utf-8') #python 2
        except:
            strts = str(ts, 'utf-8')
            
        print(strts)
        
        
        result = postKodiRequest("tagesschau", None, strts)
    except Exception as e:
        result = {'result': False, 'message' : 'Tagesschau kann nicht gestartet werden '+str(e)}
    return result
    
def getErrorMessage(dic):    
    try:
        return dic["data"]["error"]["message"]
    except:
        try:
            return dic['message']['message']        
        except:
            try:
                return dic['message']
            except:
                return "Unbekannt"


def kodiPlayMovieId(movieId):
    result = postKodiRequest("open", "movie", movieId)   
    if result['result']: 
        result = { 'result': True,  'message' : "Starte " + str(movieId)}
    else:   
        result = { 'result': False,  'message' : 'Konnte Film nicht starten. Grund: ' + getErrorMessage(result) }
    return result  
    
def kodiPlayMovie(movieTitle):    
    items = getPlayableItems("movies", movieTitle)
    item = getBestMatch(movieTitle, items)        
        
    #play item
    if len(item)>0:  
        result =  kodiPlayMovieId(item["movieid"])
        if 'result' in result and result['result']: 
            result = { 'result': False,  'message' : "Starte den Film " +  item["label"] }   
    else:
        result = { 'result': False,  'message' : "Keinen Film mit Namen " + str(movieTitle) +  " gefunden"}
    return result