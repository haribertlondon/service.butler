# -*- coding: utf-8 -*-

import socket

LISTEN_CHUNKSIZE = 1024
LISTEN_SAMPLERATE = 44100
LISTEN_MIC_INDEX = None

LISTEN_TIMEOUT = None
LISTEN_PHRASETIMEOUT = 5.0 #makes sense with snowboy hotword detection
LISTEN_PURE_PHRASE_TIME = 0.4 #short expression, like for "Play"
LISTEN_PAUSE_THRESHOLD = 0.5 #pause after phrase
LISTEN_PHRASE_MIN_TIME = 1.5
LISTEN_ENERGY_THRESHOLD = 300 #will be modified dynamically. This is the start value
LISTEN_SENSITIVITY = "0.9" # was "0.4" in the example


HTTP_TIMEOUT = 20

LISTEN_WRITEWAV = "speech.wav"
LISTEN_HOTWORD = ["kodi", "jarvis"]
LISTEN_GOOGLEKEY = ""
LISTEN_LANGUAGE= 'de-DE' #["en-US",'de']
HTTP_KODI_IP = 'localhost:8080'#'192.168.0.60:8080'
LISTEN_SNOWBOY_RESOURCE = './resources/lib/snowboyrpi8/'
LISTEN_SNOWBOY_MODELS = ['./resources/lib/snowboyrpi8/kodi.pmdl']
LISTEN_SNOWBOY = ( LISTEN_SNOWBOY_RESOURCE , LISTEN_SNOWBOY_MODELS   )

def hasSnowboy():
    s = socket.gethostname() 
    return s != "Ankermann"

def isDebug():
    return socket.gethostname() == "Ankermann"

try:
    import xbmcaddon    
    #_url = sys.argv[0] # Get the plugin url in plugin:// notation.
    #_handle = int(sys.argv[1]) # Get the plugin handle as an integer number.
    
    ADDON = xbmcaddon.Addon('service.butler')
    
    LISTEN_GOOGLEKEY = ADDON.getSetting("LISTEN_GOOGLEKEY")    
    LISTEN_LANGUAGE = ADDON.getSetting("LISTEN_LANGUAGE")
    HTTP_KODI_IP = ADDON.getSetting("HTTP_KODI_IP")
    LISTEN_HOTWORD = ADDON.getSetting("LISTEN_HOTWORD")
    LISTEN_WRITEWAV = None
except ImportError as error:
    print("Script is not running as Kodi service")
except Exception as exception:
    print("Reading settings went wrong")
    raise
    