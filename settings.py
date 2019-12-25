# -*- coding: utf-8 -*-
LISTEN_CHUNKSIZE = 1024
LISTEN_SAMPLERATE = None 
LISTEN_MIC_INDEX = None
LISTEN_TIMEOUT = None
LISTEN_PHRASETIMEOUT = 10
HTTP_TIMEOUT = 20

LISTEN_WRITEWAV = "speech.wav"
LISTEN_HOTWORD = "kodi"
LISTEN_GOOGLEKEY = ""
LISTEN_LANGUAGE= 'de-DE' #["en-US",'de']
HTTP_KODI_IP = 'localhost:8080'#'192.168.0.60:8080'


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
    