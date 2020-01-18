# -*- coding: utf-8 -*-

import socket
import sys

LISTEN_CHUNKSIZE = 1024
LISTEN_SAMPLERATE = 44100
LISTEN_MIC_INDEX = None

LISTEN_TIMEOUT = None
LISTEN_PHRASE_TOTALTIMEOUT = 5.0 #makes sense with snowboy hotword detection
LISTEN_PHRASE_PUREPHRASETIME = 0.6 #short expression, like for "Play" 0.65 is too long
LISTEN_PHRASE_PAUSE_THRESHOLD = 1.0 #pause after phrase
LISTEN_PHRASE_MIN_TIME = LISTEN_PHRASE_PUREPHRASETIME + LISTEN_PHRASE_PAUSE_THRESHOLD

LISTEN_ADJUSTSILENCE_DURATION = 1.0
LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_RATIO = 1.5
LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_FAST_TAU = 0.8 #seconds 0.8sec was taken from snowboy example/source code
LISTEN_ADJUSTSILENCE_DYNAMIC_ENERGY_DAMPING_SLOW_TAU = 15 #seconds 

LISTEN_ENERGY_THRESHOLD = 300 #will be modified dynamically. This is the start value
LISTEN_SNOWBOY_SENSITIVITY = "0.59" #"0.56" # was "0.4" in the example
LISTEN_VERBOSE_TIMEOUT = 103.0
LISTEN_AUDIO_GAIN = 1.3
LISTEN_HOTWORD_METHODS = 1 #1=snowboy 2=sphinx 3=bothOR 4=bothAND
LISTEN_HOTWORD_DURATION = 0.8
x=1e-33 #x=0.5e-10
LISTEN_SPHINX_KEYWORDS = [("kodi", x)] #LISTEN_SPHINX_KEYWORDS = [("parker", x), ("kodi", x), ("hermine", x)]


MAIL_SERVER_SETTINGS_FILE = '../mail.jpg'

HTTP_TIMEOUT = 20

LISTEN_WRITEWAV = "speech.wav"
LISTEN_HOTWORD = ["termin", "hermine", "termine", "kodi", "jarvis", "corrin", "gaudi", "audi", "tony", "rowdy", "godi", "tonie", "toni", "gorie", "gori","curry", "(k|g|p|h)(au|o|ow)(l|d|r|rr|n)(i|y|ie)", "pauli", "howdy"]
LISTEN_GOOGLEKEY = ""
LISTEN_LANGUAGE= 'de-DE' #["en-US",'de']
HTTP_KODI_IP = 'localhost:8080'#'192.168.0.60:8080'
LISTEN_SNOWBOY_RESOURCE = './resources/lib/snowboyrpi8/resources/common.res'
LISTEN_SNOWBOY_MODELS = ['./resources/lib/snowboyrpi8/kodi.pmdl']

OUTPUT_VOLUME_DB = -20

def setSensitivity(s):
    global LISTEN_SNOWBOY_SENSITIVITY
    try:
        x = float(s)
        
        if x>1:
            x = x / 100.0
        
        if x<1.0:
            LISTEN_SNOWBOY_SENSITIVITY = str(x)
            print("Setting sensitivity to ", LISTEN_SNOWBOY_SENSITIVITY)
        else:
            print("Not able to change sensitivity", s)
            raise Exception("Number not between 0 and 1")    
        return { 'result': True,  'message' : "OK"}
    except Exception as e:
        print(e)
        return { 'result': False,  'message' : "Kann Empfindlichkeit nicht aendern: " + str(e)}
    
        
        
def isPython3():
    return (sys.version_info > (3, 0))

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
    
