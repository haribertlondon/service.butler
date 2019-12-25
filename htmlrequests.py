# -*- coding: utf-8 -*-
import sys
import json
import settings

if (sys.version_info > (3, 0)):
    import urllib.request as urlrequest #@UnusedImport
else:
    import urllib2 as urlrequest #@UnresolvedImport @Reimport
   
def downloadBinary(url, post): 
    print(url, post)  
    try:
        req = urlrequest.Request(url)        
        #req.add_header('User-Agent', '')
        req.add_header('Content-Type','application/json')
        r = urlrequest.urlopen(req, data = post, timeout=settings.HTTP_TIMEOUT)#, headers = {'content-type': 'application/json'})
        html = r.read()
        print("Received html response: ", str(html))
    except Exception as e:
        print(("Error with link "+str(url) + ' Exception: ' + str(e)))        
        html = ""     
        
    return html


def downloadJsonDic(url, post):
    html = downloadBinary(url, post)  
    print(html)
    js = json.loads(html)
    print(js)
    return js

def downloadStr(url, post):
    html = downloadBinary(url, post)    
    return html.decode('utf-8')

def htmlPostRequest(url, post):
    js = downloadJsonDic(url, post)
    
    if 'result' in js and js['result'] is not None and (js['result'] == 'OK' or isinstance(js['result'],dict) ):  #js.get('result','Key-Error') == 'OK'  :
        return { 'result': True,  'message' : 'OK', 'data': js['result'] }
    else:   
        return { 'result': False,  'message' : str(js) }