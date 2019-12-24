import difflib 
import htmlrequests

def getKodiUrl(command, typeStr, searchStr):    
    hostname = 'http://192.168.0.161:8080/jsonrpc'
    url = hostname    
    post = None
    if command == "search": 
        if typeStr == "movies":
            post = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties" : ["dateadded", "lastplayed", "year", "rating", "playcount", "genre"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}'
        elif typeStr == "tvshows":
            post = '{ "jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": { "filter": {"operator": "contains", "field": "title", "value": "'+str(searchStr)+'"}, "properties": ["dateadded", "lastplayed",  "year", "rating", "playcount"],           "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libTvshows"}'
    elif command == "play":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1, "play":true },"id":1}'        
    elif command == "pause":
        post = '{ "jsonrpc": "2.0", "method": "Player.PlayPause", "params": {"playerid": 1 ,"play":false},"id":1}'
    elif command == "open":
        post = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": {"movieid": '+str(searchStr)+ '} }, "id": 1 }' #geht!!!
    elif command == 'info':
        post = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "season", "episode", "showtitle", "rating"], "playerid": 1 }, "id": "VideoGetItem"}'
     
    post = str.encode(post)
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
    
def postKodiRequest(url, post):
    result = htmlrequests.htmlPostRequest(url, post)
    if result['result']: 
        return result
    else:   
        return { 'result': False,  'message' : 'Fehlgeschlagen. Grund: ' + str(result['message']) }
    
def kodiPlay():
    (url, post) = getKodiUrl("play", None, None)    
    return postKodiRequest(url, post)   

def kodiPause():
    (url, post) = getKodiUrl("pause", None, None)    
    return postKodiRequest(url, post)

def kodiGetCurrentPlaying():
    (url, post) = getKodiUrl("info", None, None)
    result = postKodiRequest(url, post)
    info = 'Spiele gerade ' + result['data']['item']['title'] 
    try:
        info = info + ' mit ' + str(round(result['data']['item']['rating'],1)).replace(".",",") + ' Sternen'
    except:
        pass
    return { 'result': False,  'message' : info}
    
    
def kodiOpenMovie(movieTitle):    
    items = getPlayableItems("movies", movieTitle)
    item = getBestMatch(movieTitle, items)        
        
    #play item
    if len(item)>0:  
        (url, post) = getKodiUrl("open", None, item["movieid"])        
        result = postKodiRequest(url, post) 
        if result['result']: 
            result = { 'result': True,  'message' : "Starte " + str(item["label"])}
        else:   
            result = { 'result': False,  'message' : result['message'] + ' Film ' + str(item["label"]) + ' gestartet'}        
    else:
        result = { 'result': False,  'message' : "Keinen Film mit Namen " + str(movieTitle) +  " gefunden"}
    return result