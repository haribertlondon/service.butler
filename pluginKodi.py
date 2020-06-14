# -*- coding: utf-8 -*-
import difflib 
import htmlrequests
import settings
import sys
import json        
import time
import random
import re
        

def getKodiUrl(command, typeStr, searchStr, playerID= None, playlistID = None):
    hostname = 'http://' + settings.HTTP_KODI_IP + '/jsonrpc'
    url = hostname    
    post = None
    
    if playerID is None or playerID < 0:
        playerID = 1
    
    if playlistID is None:
        playlistID = 0
    
    if command == "search": 
        if typeStr == "movies" or typeStr == "movie" or typeStr == "movieid":
            post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : ["playcount"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows" or typeStr == "tvshowid":
            post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": { "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": '+str(playerID)+', "play":true },"id":1}'        
    elif command == "pause":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": '+str(playerID)+' ,"play":false},"id":1}'
    elif command == "openfile":
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": {"item":{"file":"'+searchStr+'"}},"id":1}'
    elif command == "opendirectory":
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": {"item":{"directory":"'+searchStr+'"}, "options":{"shuffled":true}},"id":1}'
    elif command == "open":
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": '+json.dumps(searchStr)+' ,"options":{"resume": true} }, "id": 1 }'        
    elif command == 'getRandomMovieByGenre':
        post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : ["playcount", "genre", "trailer"], "limits": { "start" : 0, "end": 10 }, "filter": {"field": "genre", "operator": "contains", "value": "'+searchStr+'"}, "sort": { "order": "ascending", "method": "random", "ignorearticle": true } }, "id": "libMovies"}'
    elif command == 'getRandomMovieByGenreUnwatched':
        post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : ["playcount", "genre", "trailer"], "limits": { "start" : 0, "end": 10 }, "filter": {"and": [{"field": "playcount", "operator": "is", "value": "0"}, {"field": "genre", "operator": "contains", "value": "'+searchStr+'"}]}, "sort": { "order": "ascending", "method": "random", "ignorearticle": true } }, "id": "libMovies"}'
    elif command == 'info':
        post = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "season", "episode", "showtitle", "rating"], "playerid": '+str(playerID)+' }, "id": "VideoGetItem"}'
    elif command == 'stop':
        post = '{ "jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid": '+str(playerID)+' },"id":1}'
    elif command == 'lastepisode':         
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes", "params": { "tvshowid": '+str(searchStr)+', "properties": ["title", "rating", "season"],  "limits": { "start" : 0, "end": 10 },   "filter": {"and": [{"field": "playcount", "operator": "is", "value": "0"}, {"field": "season", "operator": "greaterthan", "value": "0"}]},    "sort": { "order": "ascending", "method": "episode" } }, "id": "libEpisodes"}'        
    elif command == 'lasttvshow':            
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {  "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "descending", "method": "lastplayed" } }, "id": "libTvshows"}'    
    elif command == 'lastmovie':            
        post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetMovies", "params": {  "properties": ["resume" ,"dateadded", "lastplayed",  "year", "rating", "playcount"],   "limits": { "start" : 0, "end": 100 },         "sort": { "order": "descending", "method": "lastplayed" } }, "id": "libMovies"}'
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
        post = '{"jsonrpc": "2.0", "method": "Player.Seek", "id": 1, "params": { "playerid": '+str(playerID)+', "value": { "seconds": '+str(searchStr)+' } }}'
    elif command == 'clearPlaylist' :    
        post = '{"jsonrpc": "2.0", "id": 0, "method": "Playlist.Clear", "params": {"playlistid": '+str(playlistID)+'}}'
    elif command == 'getPlaylist':
        post = '{"jsonrpc":"2.0","method":"Player.GetProperties","params":{ "playerid": '+str(playerID)+', "properties": ["playlistid"]}, "id":1}'
    elif command == 'addPlaylist':
        post = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": {"playlistid": '+str(playlistID)+', "item": '+json.dumps( searchStr )+'  }, "id": 1 }'
    elif command == 'playPlaylist':
        post = '{"jsonrpc": "2.0", "id": 1, "method": "Player.Open", "params": {"item": {"playlistid": '+str(playlistID)+', "position":'+str(searchStr)+' } ,"options":{"resume": true}} }'    
    elif command == 'getTrailer':
        post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : ["playcount", "genre", "trailer"], "limits": { "start" : 0, "end": 10 }, "filter": {"field": "genre", "operator": "contains", "value": "'+searchStr+'"}, "sort": { "order": "ascending", "method": "random", "ignorearticle": true } }, "id": "libMovies"}'
    elif command == 'favorites':
        post = '{"jsonrpc": "2.0", "method": "Favourites.GetFavourites", "params": { "properties" : ["path", "windowparameter"]}, "id": "libMovies"}'
    elif command == 'podcast':
        post = '{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": { "directory" : "'+searchStr+'","media":"files"}, "id": "libMovies"}'
    else:
        print('Command not found', command)
     
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
    try:
        return getActivePlayerID_exception()
    except Exception as e:
        print(e)
        return 1 #it seems in my case, that 1 is the default playerID
    
def getActivePlayerID_wait(maxWait): #maxWait in seconds
    for i in range(maxWait):
        try:
            playerID = getActivePlayerID_exception()
        except: 
            print("No player id. Waiting..."+str(i))
            time.sleep(1) #wait until movie has started. otherwise, playerId is not known. However, the movie has already started
        else:
            return playerID
    return None
    
def getActivePlayerID_exception():
    response = postKodiRequest("playerID", None, None)
    return response["data"][0]["playerid"]
    
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
    result = kodiPlayTVShowLastEpisodeByName(title)
    if not result.get('result', False):
        result = kodiPlayMovie(title)
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

def kodiAddToPlaylist(itemID, playlistID, typeStr):
    return postKodiRequest('addPlaylist', typeStr, itemID, playlistID = playlistID)

def kodiPlayPlaylist(playlistID, position = 0):
    return postKodiRequest('playPlaylist', None, position, playlistID = playlistID)        

def kodiPlayItemsAsPlaylist(items, typeStr):    
    try:
        
        #make an array out of items
        items = [items] if not isinstance(items, list) else items
        #kodiClearPlaylist(1)
        items2 = []
        for item in items:
            if 'trailer' in item and typeStr == 'trailer':
                if len(item['trailer'])>0:    
                    items2.append({'file' : item['trailer']}) #items2.append({ 'file' : 'plugin://plugin.video.youtube/play/?video_id='+re.search('videoid=(.*)', item['trailer']).group(1)  })                    
            elif 'file' in item:                
                items2.append({ 'file': item['file'] })
            elif 'episodeid' in item:                
                items2.append({ 'episodeid': item['episodeid']})
            elif 'movieid' in item:                
                items2.append({'movieid' : item['movieid']})

        items = items2
        
        if len(items)>0:
            result = postKodiRequest('open', None, items[0])

            if result['result'] and len(items)>1:
                
                playerID = getActivePlayerID_wait(15) #max wait 15 sec
            
                playlistIDdic = kodiGetActivePlaylistID(playerID)
                print("Playlists found ", playlistIDdic)        
                
                try:
                    playlistID = playlistIDdic['data']['playlistid']
                except:
                    playlistID = 0
                    
                playlistIDs = list(set([0,1,playlistID]))
                
                for i in playlistIDs: #add to playlist number 0 and 1, since sometimes the playlist id changes. The code above also sometimes does not work!
                    result = kodiAddToPlaylist(items[1:], i, typeStr)
        else:
            raise Exception("No items found")
            
    except Exception as e:
        print(e)
        print("Ignoring these failures. We now try to run the episode")
     

    return result 

    
def kodiPlayTVShowLastEpisodeById(tvshowid):    
      
    result = getLastEpisode(tvshowid)
    
    if 'result' in result and result['result'] and 'data' in result and 'episodes' in result['data'] and len(result['data']['episodes'])>0: 
        #result = { 'result': True,  'message' : "Starte " + str(result["data"])}
        return kodiPlayItemsAsPlaylist(result['data']['episodes'],"episodeid")
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
    
def kodiPlayLastMovie():            
    result = postKodiRequest("lastmovie", None, None)    
    try:
        lst = []
        for movie in result['data']['movies']: 
            if movie['resume']['position'] > 0:
                lst.append(movie)
        if len(lst)  > 0:         
            return kodiPlayItemsAsPlaylist(lst, "movieid")
        else:
            return { 'result': False,  'message' : 'Keinen letzten Film gefunden'  } 
    except Exception as e:
        print(e)
        return { 'result': False,  'message' : 'Keinen letzten Film gefunden'  } 
    
def kodiPlayRandomMovieByGenre(genre, unwatched, onlyTrailer):
    genre = genre.replace("-"," ").lower()
    if "Action".lower() in genre:
        genre = "Action"
    if "Abenteuer".lower() in genre:
        genre = "Abenteuer"
    if "Familie".lower() in genre:
        genre = "Familie"
    if "Fantasy".lower() in genre:
        genre = "Fantasy"
    if "Mystery".lower() in genre:
        genre = "Mystery"
    if "Science".lower() in genre:
        genre = "Science Fiction"
        
    if unwatched:
        result = postKodiRequest("getRandomMovieByGenreUnwatched", None, genre)
    else:
        result = postKodiRequest("getRandomMovieByGenre", None, genre)  
          
    try:
        movies = result['data']['movies']        
        if len(movies)>0:
            if onlyTrailer:
                return kodiPlayItemsAsPlaylist(movies, "trailer")
            else:
                return kodiPlayItemsAsPlaylist(movies, "movieid")
        else:
            raise Exception("No movies found")
    except Exception as e:
        print(e)
        return result
  
def kodiPlayPodcast():
    url = r"plugin://plugin.video.itunes_podcasts/video/podcast/items/104913043/" #swr2 wissen
    
    try:
        js = postKodiRequest("podcast", None, url)
        lst = js["data"]["files"]
        random.shuffle(lst)
        lst = lst[:10]
        return kodiPlayItemsAsPlaylist(lst, None)
    except:
        js = {'result': False, 'message' : 'Keinen Podcast gefunden'}
        #raise Exception("Kein Podcast gefunden")
    return js
        
    
 
def kodiPlayYoutube(searchStr):
    searchStr = searchStr.replace(" ","+")
    try:
        url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=12&order=relevance&q='+searchStr+'&key=AIzaSyCWRdUIzgMLnhoyX1BcRbm9iwiBRKmqM1A'
        url = re.sub("A$","0", url)
        js = htmlrequests.downloadJsonDic(url,None)
        print(js)
        #videoId = None
        lst = []
        for item in js['items']:
            if 'videoId' in item['id']:
                lst.append( { 'file' : 'plugin://plugin.video.youtube/play/?video_id='+item['id']['videoId']  } )

        if len(lst) > 0:
            result = kodiPlayItemsAsPlaylist(lst, "file")
        else:
            js = {'result': False, 'message' : 'Kein Youtube Video gefunden'}
            raise Exception("Kein Video gefunden")
            
            
    except Exception as e:
        print("Youtube Exception: ",e)
        result = js
    
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
            ts = [x for x in js['latestBroadcastsPerType'] if showStr in x['title'] ][0]['sophoraId'] 
        print(ts)
                
        if (sys.version_info > (3, 0)):
            strts = ts #str(ts, 'utf-8')
        else:
            strts = ts.encode('utf-8') #python 2
        
        result = postKodiRequest("tagesschau", None, strts)
    except Exception as e:
        print(e)
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

def kodiPlayAvailableMovieTrailers():
    return kodiPlayRandomMovieByGenre("", False, True)

def kodiPlayItem(movieId):
    result = postKodiRequest("open", None, movieId)   
    if result['result']: 
        result = { 'result': True,  'message' : "Starte " + str(movieId)}
    else:   
        result = { 'result': False,  'message' : 'Konnte Film nicht starten. Grund: ' + getErrorMessage(result) }
    return result

def kodiPlayFile(filepath):
    result = postKodiRequest("openfile", None, filepath)   
    if result['result']: 
        result = { 'result': True,  'message' : "Starte " + str(filepath)}
    else:   
        result = { 'result': False,  'message' : 'Konnte Datei nicht starten. Grund: ' + getErrorMessage(result) }
    return result

def kodiPlayDirectory(filepath):
    result = postKodiRequest("opendirectory", None, filepath)   
    if result['result']: 
        result = { 'result': True,  'message' : "Starte " + str(filepath)}
    else:   
        result = { 'result': False,  'message' : 'Konnte Film nicht starten. Grund: ' + getErrorMessage(result) }
    return result
    
def kodiPlayMovie(movieTitle):    
    items = getPlayableItems("movies", movieTitle)
    item = getBestMatch(movieTitle, items)        
        
    #play item
    if len(item)>0:  
        result =  kodiPlayItem({'movieid': item["movieid"]} )
        if 'result' in result and result['result']: 
            result = { 'result': True,  'message' : "Starte den Film " +  item["label"] }
    else:
        result = { 'result': False,  'message' : "Keinen Film mit Namen " + str(movieTitle) +  " gefunden"}
    return result

def kodiPlayFavorites(favTitle):    
    
    result = postKodiRequest('favorites', "", "")
    #if 'favourites' in a:
    #    a = a[]
    if 'result' in result and result['result'] and 'data' in result:
        lst = result['data'].get("favourites",[])
        for item in lst:
            if favTitle == item.get('title',''):
                if "path" in item:
                    return kodiPlayFile(item['path'])
                elif "windowparameter" in item:                    
                    return kodiPlayDirectory(item['windowparameter'])
                else:
                    return { 'result': False,  'message' : "Favoriten haben unbekanntes Format"}
                    
                
            
    return { 'result': False,  'message' : u"Konnte die Favorite "+str(favTitle)+u" nicht öffnen"}

def kodiSurprise():
    for _ in range(1,10):
        result = kodiTrySurprise([0,1,2,3,4,5,6,7,8,9,10,11])
        if result.get('result', True):
            return result
    return { 'result': False,  'message' : u"Konnte keine zufällige Medien starten"}

def kodiSurpriseTalk():
    for _ in range(1,10):
        result = kodiTrySurprise([2,3])
        if result.get('result', True):
            return result
    return { 'result': False,  'message' : u"Konnte keine zufällige Medien starten"}

def kodiTrySurprise(selection):
    a = selection[random.randint(0, len(selection))]
    if a == 0:        
        return kodiPlayYoutube("The Daily Show")
    elif a == 1:
        return kodiPlayYoutube("Neue KINO TRAILER")
    elif a == 2:
        return kodiPlayYoutube("Maybrit Illner")
    elif a == 3:
        return kodiPlayYoutube("Markus Lanz")
    elif a == 4:
        return kodiPlayYoutube("Heute Show")
    elif a == 5:
        return kodiPlayYoutube("Extra 3")
    elif a == 6:
        return kodiPlayYoutube("Dokumentation deutsch")
    elif a == 7:
        return kodiPlayTagesschau('tagesthemen')
    elif a == 8:
        return kodiPlayTagesschau('tagesschau')
    elif a == 9:
        return kodiPlayAvailableMovieTrailers()
    elif a == 10:
        return kodiPlayFavorites("Concerts")
    elif a == 11:
        return kodiPlayYoutube("Spiegel tv")
        
    return { 'result': False,  'message' : u"Konnte keine zufällige Medien starten"}
 
        
  

if __name__ == "__main__":
    #kodiPlayTagesschau("tagesthemen")
    #kodiPlayMovieOrSeries("Modern Family")
    #kodiPlayYoutube("Extra 3")
    #idx = getActivePlayerID()
    #kodiGetCurrentPlaying()
    #kodiStop()
    #a=kodiPlayLastTvShow()
    #a=kodiPlayAvailableMovieTrailers()
    #playerID = getActivePlayerID()
    #a = kodiGetActivePlaylistID(playerID)
    #print(a)
    #a = kodiPlayYoutube("The Daily Show")
    a = kodiPlayPodcast()
    #a = kodiPlayFavorites("Concerts")
    #a = kodiPlayFavorites("SWR2")
    print(">",a)
    #a = kodiPlayLastMovie()
    #print(a)
