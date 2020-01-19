from urllib.request import quote as urlquote
import requests
import re
import pluginKodi
import htmlrequests
import os 
import datetime

def getFilename():    
    uniqStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    defaultFilename = os.path.dirname(os.path.realpath(__file__))+"/browser"+uniqStr+".jpg"
    defaultFilename = (r'|'.join((r'|'.join(defaultFilename.split('/'))).split("\\"))).replace("|","\/")
    return defaultFilename

def getImageUrl(url = 'http://yahoo.com'):
    qurl = urlquote(url, safe='')
    fullurl = 'http://api.screenshotlayer.com/api/capture?access_key=b5ac6f204eb21a3e1ea452efaddd82f3&viewport=1440x900&format=jpg&url='+qurl
    return fullurl
    
def getRedirect(url):
    r = requests.head(url, allow_redirects=True) #delivers http://www.google.com/url?q=https://de.pinout.xyz/
    print(r.url)    
    url = re.sub("^.*?q=","",r.url) #cut google-part, get pure webpage
    print(url)
    return url

def runUrl(url, filename = None):
    if filename is None:
        filename = getFilename()
    imageUrl = getImageUrl(url)
    a = htmlrequests.downloadToFile(imageUrl, None, filename)
    if a:
        return pluginKodi.postKodiRequest("rawopen", None, filename, None, None)
    else:
        return {'result': False, 'message': 'Konnte url nicht öffnen'}

def runGoogleLucky(s, filename = None):    
    s = urlquote(s, safe='')
    url = 'http://www.google.com/search?q='+s+'&btnI'
    print(url)    
    url = getRedirect(url)
    print("Redirect", url)
    return runUrl(url, filename)

if __name__ == "__main__":
    runGoogleLucky("raspi pinout")    
    print("Finished")