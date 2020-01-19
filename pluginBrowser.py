# -*- coding: utf-8 -*-
import sys
if (sys.version_info > (3, 0)):
    import urllib.request as urlrequest #@UnusedImport 
else:
    import urllib2 as urlrequest #@UnresolvedImport @Reimport

import requests
import re
import pluginKodi
import htmlrequests
import os 
import datetime

def getFilename():    
    uniqStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    defaultFilename = os.path.dirname(os.path.realpath(__file__))+"/browser"+uniqStr+".jpg"
    defaultFilename2 = (r'|'.join((r'|'.join(defaultFilename.split('/'))).split("\\"))).replace("|","\/")
    return (defaultFilename, defaultFilename2)

def getImageUrl(url = 'http://yahoo.com'):
    qurl = urlrequest.quote(url, safe='')
    fullurl = 'http://api.screenshotlayer.com/api/capture?access_key=b5ac6f204eb21a3e1ea452efaddd82f3&viewport=1440x900&format=jpg&url='+qurl
    return fullurl
    
def getRedirect(url):
    r = requests.head(url, allow_redirects=True) #delivers http://www.google.com/url?q=https://de.pinout.xyz/
    print(r.url)    
    url = re.sub("^.*?q=","",r.url) #cut google-part, get pure webpage
    print(url)
    return url

def runUrl(url, filename = None, filenameQuoted=None):
    if filename is None:
        (filename, filenameQuoted) = getFilename()
    imageUrl = getImageUrl(url)
    a = htmlrequests.downloadToFile(imageUrl, None, filename)
    if a:
        return pluginKodi.postKodiRequest("rawopen", None, filenameQuoted, None, None)
    else:
        return {'result': False, 'message': u'Konnte URL nicht öffnen'}

def runGoogleLucky(s, filename = None):    
    s = urlrequest.quote(s, safe='')
    url = 'http://www.google.com/search?q='+s+'&btnI'
    print(url)    
    url = getRedirect(url)
    print("Redirect", url)
    return runUrl(url, filename)

if __name__ == "__main__":
    #runGoogleLucky("raspi pinout")    
    a = getFilename()
    print(a)
    print("Finished")
