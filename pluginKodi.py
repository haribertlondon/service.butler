# -*- coding: utf-8 -*-
import difflib 
import htmlrequests
import settings
import sys

def getKodiUrl(command, typeStr, searchStr, playerID= None, playlistID = None):
    hostname = 'http://' + settings.HTTP_KODI_IP + '/jsonrpc'
    url = hostname    
    post = None
    
    if playerID is None:
        playerID = 1
    
    if playlistID is None:
        playlistID = 0
    
    if command == "search": 
        if typeStr == "movies" or typeStr == "movie":
            post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties" : ["dateadded", "lastplayed", "year", "rating", "playcount", "genre"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows":
            post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {                                                                                      "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": '+str(playerID)+', "play":true },"id":1}'        
    elif command == "pause":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": '+str(playerID)+' ,"play":false},"id":1}'
    elif command == "open":
        if typeStr == 'movies' or typeStr == 'movie': 
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"movieid": '+str(searchStr)+ '} ,"options":{"resume": true} }, "id": 1 }'
        elif typeStr == 'tvshows' or typeStr == 'episodes' or typeStr == 'episode': 
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"episodeid": '+str(searchStr)+ '} ,"options":{"resume": true} }, "id": 1 }'
        else:
            post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"playlistid": ' +str(searchStr) + '} ,"options":{"resume": true} }, "id": 1 }'
                                                                
    elif command == 'info':
        post = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "season", "episode", "showtitle", "rating"], "playerid": '+str(playerID)+' }, "id": "VideoGetItem"}'
    elif command == 'stop':
        post = '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid": '+str(playerID)+' },"id":1}'
    elif command == 'lastepisode':         
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes", "params": { "tvshowid": '+str(searchStr)+', "properties": ["title", "rating", "season"],  "limits": { "start" : 0, "end": 10 },   "filter": {"and": [{"field": "playcount", "operator": "is", "value": "0"}, {"field": "season", "operator": "greaterthan", "value": "0"}]},    "sort": { "order": "ascending", "method": "episode" } }, "id": "libEpisodes"}'        
    elif command == 'lasttvshow':            
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {  "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "descending", "method": "lastplayed" } }, "id": "libTvshows"}'    
    elif command == 'tagesschau':                   
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"file": "plugin://plugin.video.tagesschau/?action=play_video&feed=latest_broadcasts&tsid='+searchStr+'"  } }, "id": 1 }'
    elif command == 'youtube':
        post = '{"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"plugin://plugin.video.youtube/play/?video_id='+searchStr+'"}},"id":"1"}'
    elif command == 'radio':
        post = '{"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"plugin://plugin.audio.radio_de/station/'+searchStr+'"}},"id":"1"}'
    elif command == 'showmessage':
        post = '{"jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title": "Info", "message": "' + searchStr + '"}, "id": 1}'
    elif command == 'playerID':
        post = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
    elif command == 'volumeup':
        post = '{ "jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": "increment" }, "id": 1 }'
    elif command == 'volumedown':
        post = '{ "jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": "decrement" }, "id": 1 }'
    elif command == 'getVolume':
        post = '{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params" : { "properties" : [ "volume", "muted" ] }, "id" : 1 }'
    elif command == 'setVolume':
        post = '{ "jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": '+searchStr+' }, "id": 1 }'
    elif command == 'screensaver':
        post = '{"jsonrpc":"2.0","method":"GUI.ActivateWindow","id":1,"params":{"window":"screensaver"}}'
    elif command == 'next':
        post = '{ "jsonrpc": "2.0", "method": "Player.GoTo", "id": 1, "params": { "playerid": '+str(playerID)+', "to":"next"} }'
    elif command == 'previous':
        post = '{ "jsonrpc": "2.0", "method": "Player.GoTo", "id": 1, "params": { "playerid": '+str(playerID)+', "to":"previous"} }'
    elif command == 'seek':
        post = '{"jsonrpc": "2.0", "method": "Player.Seek", "id": 1, "params": { "playerid": '+str(playerID)+', "value": { "seconds": '+searchStr+' } }}'
    elif command == 'clearPlaylist' :    
        post = '{"jsonrpc": "2.0", "id": 0, "method": "Playlist.Clear", "params": {"playlistid": '+str(playlistID)+'}}'
    elif command == 'getPlaylist':
        post = '{"jsonrpc":"2.0","method":"Player.GetProperties","params":{ "playerid": '+str(playerID)+', "properties": ["playlistid"]}, "id":1}'
    elif command == 'addPlaylist':
        if typeStr == 'movies' or typeStr == 'movie': 
            post = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "playlistid": '+str(playlistID)+', "item": {"movieid": '+str(searchStr)+ '}  }, "id": 1 }'            
        elif typeStr == 'tvshows' or typeStr == 'episodes' or typeStr == 'episode': 
            post = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": {"playlistid": '+str(playlistID)+', "item": {"episodeid": '+str(searchStr)+ '}  }, "id": 1 }'                    
    elif command == 'playPlaylist':
        post = '{"jsonrpc": "2.0", "id": 2, "method": "Player.Open", "params": {"item": {"playlistid": '+str(playlistID)+', "position":'+str(searchStr)+' } ,"options":{"resume": true}} }'    
    else:
        print('Command not found', command)
    #elif command == 'tagesschau':                   
    #    post = '{ "jsonrpc": "2.0", "method": "Addons.ExecuteAddon","params":{"addonid":"plugin.video.tagesschau","params":{"action":"list_feed","feed":"latest_broadcasts" }}, "id": 1 }'
    #elif command == 'getplaylist':
    #    post = '{"jsonrpc": "2.0", "method": "Playlist.GetItems", "params": { "properties": [ "runtime", "showtitle", "season", "title", "artist", "file" ], "playlistid": 1}, "id": 1}'           
    
    try:   
        post = str.encode(post) # set to byte array
    except:
        post = post.encode("utf-8")
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
        return { 'result': False,  'message' : 'Fehlgeschlagen. '} # + getErrorMessage(result) }
    
def getActivePlayerID():
    response = postKodiRequest("playerID", None, None)
    try:
        return response["data"][0]["playerid"]
    except Exception as e:
        print(e)
        return 1 #it seems in my case, that 1 is the default playerID
    
def postKodiRequest(command, typeStr, searchStr, playerID = None, playlistID = None):
    (url, post) = getKodiUrl(command, typeStr, searchStr, playerID = playerID, playlistID = playlistID) 
    return postKodiRequest_Internal(url, post)

def kodiChangeVolume(change):
    response = postKodiRequest("getVolume", None, None)
    try:        
        x = response['data']['volume']+change
        if x < 0:
            x = 0
        elif x >100:
            x = 100
        return postKodiRequest("setVolume", None, str(x))
    except Exception as e:
        print(e)
        return response
    
def kodiPlayMovieOrSeries(title):
    result = kodiPlayMovie(title)
    if not result.get('result', False):
        result = kodiPlayTVShowLastEpisodeByName(title)
    if not result.get('result', False):
        result = { 'result': False,  'message' : "Keinen Film oder Serie mit Namen " + str(title) +  " gefunden"}
    return result

def kodiVolumeDown():
    return kodiChangeVolume(-10)

def kodiVolumeUp():
    return kodiChangeVolume(+10)

def kodiShowMessage(s):
    return postKodiRequest("showmessage", None, s, None)   

def kodiStartScreensaver():
    return postKodiRequest("screensaver", None, None, None)

def kodiPlay(playerID = None):
    if playerID is None:
        playerID = getActivePlayerID() 
    return postKodiRequest("play", None, None, playerID)   

def kodiPause(playerID = None):   
    if playerID is None:
        playerID = getActivePlayerID() 
    return postKodiRequest("pause", None, None, playerID)  

def kodiStop(playerID = None):  
    if playerID is None:
        playerID = getActivePlayerID()
    return postKodiRequest("stop", None, None, playerID) 

def getLastEpisode(tvshowid):        
    return postKodiRequest("lastepisode", None, tvshowid)

def kodiSeek(sec, playerID = None):  
    if playerID is None:
        playerID = getActivePlayerID()
    return postKodiRequest("seek", None, sec, playerID) 

def kodiNext(playerID = None): 
    if playerID is None:
        playerID = getActivePlayerID() 
    return postKodiRequest("next", None, None, playerID) 

def kodiPrevious(playerID = None):  
    if playerID is None:
        playerID = getActivePlayerID() 
    return postKodiRequest("previous", None, None, playerID)

def kodiGetCurrentPlaying(playerID = None):
    if playerID is None:
        playerID = getActivePlayerID()
    #(url, post) = getKodiUrl("info", None, None)
    result = postKodiRequest("info", None, None, playerID)
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

def kodiGetActivePlaylistID(playerID):
    return postKodiRequest('getPlaylist', None, None, playerID = playerID)
   
def kodiClearPlaylist(playlistID):
    return postKodiRequest('clearPlaylist', None, None, playlistID = playlistID)

def kodiAddEpisodeToPlaylist(episodeID, playlistID):
    return postKodiRequest('addPlaylist', 'episode', episodeID, playlistID = playlistID)

def kodiPlayPlaylist(playlistID, position = 0):
    return postKodiRequest('playPlaylist', None, position, playlistID = playlistID)        

def kodiPlayEpisodeAsPlaylist(episodes):    
        
    try:
        episodeID = episodes[0]['episodeid']
    except Exception as e:
        print(e)
        print(episodes)
        return { 'result': False,  'message' : ' Keine Episode dieser Serie gefunden, die abgespielt werden kann. Grund: ' +str(e)  }
        
    
    result = kodiPlayEpisode(episodeID)
    
    try:
        playerID = getActivePlayerID()
                    
        playlistIDs = kodiGetActivePlaylistID(playerID)
        print("Playlists found ", playlistIDs)        
        
        try:
            playlistID = playlistIDs['data']['playlistid']
        except:
            playlistID = 1        
            
        print("Adding the rest of episodes")  
        if len(episodes)>1:
            episodes = episodes[1:] #removing first, since this is already in playlist      
            for episode in episodes:
                result = kodiAddEpisodeToPlaylist(episode['episodeid'], playlistID)
                print(result)
    except Exception as e:
        print(e)
        print("Ignoring these failures. We now try to run the episode")
     

    return result 

    
def kodiPlayTVShowLastEpisodeById(tvshowid):    
      
    result = getLastEpisode(tvshowid)
    
    if 'result' in result and result['result'] and 'data' in result and len(result['data']['episodes'])>0: 
        #result = { 'result': True,  'message' : "Starte " + str(result["data"])}
        return kodiPlayEpisodeAsPlaylist(result['data']['episodes'])
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

def kodiPlayRadio(channel):   
    channel = channel.lower()
     
    if channel == 'deutschlandfunk': 
        return postKodiRequest("radio", None, '1521')
    elif channel == 'bigfm' or channel == 'big fm':
        return postKodiRequest("radio", None, '1445')
    elif channel == 'antennekl'or channel == 'antenne' or channel == 'antenne kl' or channel == 'antenne kaiserslautern':
        return postKodiRequest("radio", None, '8367')
    elif channel == 'rpr1' or channel == 'rpr 1':
        return postKodiRequest("radio", None, '107229')
    elif channel == 'swr2' or channel == 'swr 2':
        return postKodiRequest("radio", None, '2414')
    elif channel == 'swr3' or channel == 'swr 3':
        return postKodiRequest("radio", None, '2275')
    else:
        return {'result': False, 'message': 'Channel nicht gefunden'}
    
    
 
def kodiPlayTagesschau(showStr):
    try:
        js = htmlrequests.downloadJsonDic('http://www.tagesschau.de/api/multimedia/sendung/letztesendungen100.json',b'')            
        if showStr == "tagesschau": #show latest tagesschau
            ts = js['latestBroadcast']['sophoraId']
        else:
            ts = [x for x in js['latestBroadcastsPerType'] if x['title']==showStr][0]['sophoraId'] 
        print(ts)
                
        if (sys.version_info > (3, 0)):
            strts = ts #str(ts, 'utf-8')
        else:
            strts = ts.encode('utf-8') #python 2
        
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
            result = { 'result': True,  'message' : "Starte den Film " +  item["label"] }
    else:
        result = { 'result': False,  'message' : "Keinen Film mit Namen " + str(movieTitle) +  " gefunden"}
    return result

if __name__ == "__main__":
    #kodiPlayTagesschau("tagesthemen")
    #idx = getActivePlayerID()
    #kodiGetCurrentPlaying()
    #kodiStop()
    a=kodiVolumeDown()
    print(a)
