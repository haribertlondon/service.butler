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
def speechInterprete(guess, wav):
    
    result= {'result' : False, 'message': 'Ich habe dich leider nicht verstanden.'}    
    
    if guess["error"] is not None or guess["error"] is not None and len(guess["error"])>0:
        print("Guessed expression not valid "+str(guess))
        #return result
        return {'result': False, 'message': 'Silence!'}
 
    
    global matchCounter
    matchCounter = 0
    
    a = pluginKodi.postKodiRequest("showmessage", "", guess["transcription"])
    print(a)
    
    #remove hotword at beginning
    command = guess["transcription"].lower().strip()   
    
    if isinstance(settings.LISTEN_HOTWORD, str):
        settings.LISTEN_HOTWORD = [settings.LISTEN_HOTWORD]
        
    hotword_found = False
    for hotword in settings.LISTEN_HOTWORD:     
        (command, n) = re.subn("^"+hotword,"", command, re.IGNORECASE).strip() #@UndefinedVariable
        if n>0:
            hotword_found = True

    if not hotword_found:
        return {'result': False, 'message': 'Silence!'}

    a = pluginKodi.postKodiRequest("showmessage", "", guess["transcription"])
    print(a)
        
    matches = re.findall("^(?:Echo).*", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginEcho.echoEcho()       
    
    matches = re.findall("^(Pause|Break)", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiPause()
        
    matches = re.findall("^(Stop|Halt)", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiStop()
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Play|Starte|Öffne)?(?: )?Youtube(?: mit)? (?:dem|der|den|die|das)?(.*)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayYoutube(matches[0])
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Starte)? (die )?letzte Serie( weiter)?", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):         
        result = pluginKodi.kodiPlayLastTvShow()
        
    matches = re.findall("^(?:Spiele |Spiel |Spielt |Starte |Start )?(die )?(letzte )?Tagesschau", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayTagesschau('tagesschau')  
        
    matches = re.findall("^(?:Spiele |Spiel |Spielt |Starte |Start )?(die )?(letzten |letzte )?Tagesthemen", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayTagesschau('tagesthemen')

    matches = re.findall("^(?:Spiele|Spiel|Spielt|Starte|Start|Radio|Radiosender)? (SWR[ 0-9]+|RPR[ 0-9]+|Big[ ]*FM|Antenne[ ]*K.*|Deutschland[ ]*funk)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayRadio(matches[0])
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Play|Starte|Öffne) (?:die Serie )?(.*) weiter", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayTVShowLastEpisodeByName(matches[0])         
    
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Play|Starte|Öffne) (.*)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayMovie(matches[0])
        
    matches = re.findall("^(?:Was läuft|Was läuft gerade|Info|Information)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiGetCurrentPlaying()  
        
    matches = re.findall("^(?:Play|Los|Weiter|Continue|Spiele weiter|Spiel weiter)( den Film)?$", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiPlay()

        
    return result