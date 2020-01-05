# -*- coding: utf-8 -*-
import re
import settings
import pluginKodi
import pluginEcho

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
        (command, n) = re.subn("^"+hotword,"", command, re.IGNORECASE) 
        if n>0:
            command = command.strip() 
            hotword_found = True


    if not hotword_found:
        matches = re.findall("^(Pause|Stop|Halt|Stopp|Spiel|Start|Öffne|Play|Radio|Was)", command, re.IGNORECASE) 
        if not matches:
            return {'result': False, 'message': 'Silence!'}
        else:
            print("Keyword not detected but found ", matches)

    a = pluginKodi.postKodiRequest("showmessage", "", guess["transcription"])
    print(a)

    matches = re.findall("^(?:Echo).*", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginEcho.echoEcho()

    matches = re.findall("^(Pause|Break)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPause()

    matches = re.findall("^(Stop|Halt|Stopp)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiStop()

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?Youtube(?: mit)? (?:dem|der|den|die|das)?(.*)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube(matches[0])

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?letzte Serie( weiter)?", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayLastTvShow()

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?(letzte )?Tagesschau", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesschau')

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(die )?(letzten |letzte )?Tagesthemen", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesthemen')

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(?:Radio |Radiosender )?(SWR[ 0-9]+|RPR[ 0-9]+|Big[ ]*FM|Antenne[ ]*K.*|Deutschland[ ]*funk)", command, re.IGNORECASE)    
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRadio(matches[0])

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )?(?:die Serie )?(.*) weiter", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTVShowLastEpisodeByName(matches[0])

    matches = re.findall("^(?:Spiele |Spiel |Spielt |Play |Starte |Öffne |Öffnet |Start )(.*)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayMovie(matches[0])

    matches = re.findall("^(?:Was läuft|Was läuft gerade|Info|Information)", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiGetCurrentPlaying()

    matches = re.findall("^(?:Play|Los|Weiter|Continue|Spiele weiter|Spiel weiter)( den Film)?$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlay()

    matches = re.findall("^(?:Mache |Mach )?Leiser$", command, re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiVolumeDown()

    matches = re.findall("^(?:Mache |Mach )?Lauter$", command, re.IGNORECASE) 
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
