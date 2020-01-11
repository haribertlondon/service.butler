# -*- coding: utf-8 -*-
import re
import sys
import settings
import pluginKodi
import pluginEcho
import pluginMail
import pluginUpdate

def checkMatch(match):    
    global matchCounter
    
    if match: 
        if matchCounter == 0:
            matchCounter = matchCounter + 1            
            return True
        else:
            matchCounter = matchCounter + 1
            print("Multiple match." + str(match))
            return False
    else:
        return False

def checkResult(result):
    return (result is not None and isinstance(result, dict) and 'result' in result and result['result'])     

# Examples Play The Beach
def speechInterprete(guess):
    
    result= {'result' : False, 'message': 'Ich habe dich leider nicht verstanden.'}    
    
    if guess["error"] is not None or guess["error"] is not None and len(guess["error"])>0:
        print("Guessed expression not valid "+str(guess))
        #return result
        return {'result': False, 'message': 'Silence!'}
 
    
    global matchCounter
    matchCounter = 0
    
    a = pluginKodi.kodiShowMessage(guess["transcription"])
    print(a)
    
    #remove hotword at beginning
    command = guess["transcription"].lower().strip()   
    
    if isinstance(settings.LISTEN_HOTWORD, str):
        settings.LISTEN_HOTWORD = [settings.LISTEN_HOTWORD]
        
    hotword_found = False
    for hotword in settings.LISTEN_HOTWORD:
        print("Checking for hotword ", hotword, command)     
        (command, n) = re.subn(u"^"+hotword,"", command, re.IGNORECASE) 
        if n>0:
            print("Found hotword")
            command = command.strip() 
            hotword_found = True
            break

    if hotword_found and len(command)==0: #only hotword was detected. => Do not say anything
        print("Hotword detected but no more text came. Aborting")
        return {'result': False, 'message': 'Silence!'}


    if not hotword_found:
        matches = re.findall(u"^(Pause|Stop|Halt|Stopp|Spiel|Start|Öffne|Play|Radio|Was)", command, re.IGNORECASE) 
        if not matches:
            print("No hotwords found and also no keywords")
            return {'result': False, 'message': 'Silence!'}
        else:
            print("Keyword not detected but found ", matches)

    a = pluginKodi.kodiShowMessage(guess["transcription"])
    print(a)

    matches = re.findall(u"^(?:Echo).*", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginEcho.echoEcho()

    matches = re.findall(u"^(Pause|Break)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPause()

    matches = re.findall(u"^(Stop|Halt|Stopp)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiStop()

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?Youtube(?: mit)? (?:dem|der|den|die|das)?(.*)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube(matches[0])

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?letzte Serie( weiter)?", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayLastTvShow()

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?(letzte )?Tagesschau", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesschau')

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?(letzten |letzte )?Tagesthemen", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesthemen')

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(?:Radio |Radiosender )?(SWR[ 0-9]+|RPR[ 0-9]+|Big[ ]*FM|Antenne[ ]*K.*|Deutschland[ ]*funk)", command, re.IGNORECASE)    
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRadio(matches[0])

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(?:die Serie )?(.*) weiter", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTVShowLastEpisodeByName(matches[0])

    matches = re.findall(u"^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )(.*)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayMovie(matches[0])

    matches = re.findall(u"^(?:Was läuft|Was läuft gerade|Info|Information)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiGetCurrentPlaying()

    matches = re.findall(u"^(?:Play|Los|Weiter|Continue|Spiele weiter|Spiel weiter)( den Film)?$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlay()

    matches = re.findall(u"^(Springe |Gehe )?(zu )?(Nächste |Nächster |Kommender |Folgender |Folgende |Kommende )(Film|Folge|Episode)$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiNext()

    matches = re.findall(u"^(Springe |Gehe )?(zu )?(letzter |Letzte |verherigen |vorigen )(Film|Folge|Episode)$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPrevious()
    
    matches = re.findall(u"^(Gute Nacht|Schlaf gut|Geh schlafen|Auf wiedersehen|Tschüss|Ruhe|Halts maul)$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPause()
        result = pluginKodi.kodiStartScreensaver()
        
    matches = re.findall(u"^(?:Stelle |Setze |Stell )Empfindlichkeit auf (.*)$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = settings.setSensitivity(matches[0])
        
    matches = re.findall(u"^Beende dich selbst$", command, re.IGNORECASE)
    if checkMatch(matches):
        sys.exit()
        
    matches = re.findall(u"^(Mache |Mach )ein Update$", command, re.IGNORECASE)
    if checkMatch(matches):
        pluginUpdate.performUpdate()        
        
    matches = re.findall(u"^(?:Schicke |Sende )?(?:Mail |Erinnerung |eMail |Erinnere mich )(?:an |mit )?(.*)$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginMail.sendMail(matches[0], "", settings.MAIL_SERVER_SETTINGS_FILE)
        
    matches = re.findall(u"^Spule vor$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiSeek(+30)
        
    matches = re.findall(u"^Spule zurück$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiSeek(-30)

    matches = re.findall(u"^(?:Mache |Mach )?Leiser$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiVolumeDown()

    matches = re.findall(u"^(?:Mache |Mach )?Lauter$", command, re.IGNORECASE) 
    if checkMatch(matches):
        result = pluginKodi.kodiVolumeUp()


    return result

if __name__ == "__main__":
    #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele Modern Family weiter" }    
    #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele letzte Serie weiter" }
    #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele MacGyver weiter" }
    #guess =  {"error": None, "transcription": settings.LISTEN_HOTWORD + " " + "Spiele die letzte Tagesschau" }
    #guess =  {"error": None, "transcription": "KODi weiter" }
    #guess =  {"error": None, "transcription": "Kodi Starte die letzten Tagesthemen" }
    #guess =  {"error": None, "transcription": "Kodi Youtube mit Trailer Deutsch" }
    #guess =  {"error": None, "transcription": "Kodi Echo Hallo Kristina" }
    #guess =  {"error": None, "transcription": "Kodi Spiele SWR3" }
    guess =  {"error": None, "transcription": "Kodi Leiser" }
    speechInterprete(guess)
