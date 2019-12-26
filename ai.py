# -*- coding: utf-8 -*-
import re
import settings
import pluginKodi


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
    

# Examples Play The Beach
def speechInterprete(guess, wav):
    
    result= {'result' : False, 'message': 'Ich habe dich leider nicht verstanden.'}
    
    if guess["error"] is not None or guess["error"] is not None and len(guess["error"])>0:
        print("Guessed expression not valid "+str(guess))
        return result 
    
    global matchCounter
    matchCounter = 0
    
    #remove hotword at beginning
    command = guess["transcription"].lower().strip()        
    command = re.sub("^"+settings.LISTEN_HOTWORD,"", command, re.IGNORECASE).strip() #@UndefinedVariable
    
    
    matches = re.findall("^(?:Play|Los|Weiter|Continue|Spiele weiter|Spiel weiter|Starte)( den Film)?$", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiPlay()
    
    matches = re.findall("^(Pause|Break)", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiPause()
        
    matches = re.findall("^(Stop|Halt)", command, re.IGNORECASE) #@UndefinedVariable
    if checkMatch(matches):
        result = pluginKodi.kodiStop()
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt)? (die )?letzte Serie( weiter)?", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):         
        result = pluginKodi.kodiPlayLastTvShow()
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt)?( die)?( letzte)? Tagesschau", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayTagesschau()  
        
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Play|Starte|Öffne) (?:die Serie )?(.*) weiter", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayTVShowLastEpisodeByName(matches[0])         
    
    matches = re.findall("^(?:Spiele|Spiel|Spielt|Play|Starte|Öffne) (.*)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiPlayMovie(matches[0])
        
    matches = re.findall("^(?:Was läuft|Was läuft gerade|Info|Information)", command, re.IGNORECASE)  #@UndefinedVariable  
    if checkMatch(matches):        
        result = pluginKodi.kodiGetCurrentPlaying()  
        
    return result