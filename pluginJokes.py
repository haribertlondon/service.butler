import htmlrequests
import re
import settings
import random

def downloadJokes():
    url = "http://www.witzdestages.net/tageswitz.js"
    js = htmlrequests.downloadStr(url,None)
    return js

def parseSite(html):
    result=[]
    for s in html.split("msg"):
        if bool(re.search("^\[[0-9]+\]", s)):
           
            try:
                joke = re.search(r"justify>(.*)<.*div",s).group(1)
            except Exception as e:
                print(e)
                continue
       
            try:
                if settings.isPython3():
                    from html import unescape
                    joke = unescape(joke)
                else:
                    import HTMLParser #@UnresolvedImport
                    html_parser = HTMLParser.HTMLParser()
                    joke = html_parser.unescape(joke)
            except Exception as e:
                print(e)
                
            if len(joke)>10:
                result.append(joke)
            
    return result

def getJoke(number):
    html = downloadJokes()
    jokes = parseSite(html)
    
    if number<0:
        number = random.randint(0, len(jokes)-1)
    
    return jokes[number] 

def tellJoke():   
    joke = getRandomJoke()
    return { 'result': True,  'message' : joke}

def getRandomJoke():
    return getJoke(-1)

if __name__ == "__main__":
    a = getRandomJoke()
    print(a)