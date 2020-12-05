# -*- coding: utf-8 -*-
import re
import settings
import pluginKodi
import pluginEcho
import pluginMail
import pluginUpdate
import pluginJokes
import gpio
import pluginBrowser
import pluginSystem

def checkMatch(match):    
    global matchCounter
    
    if match: 
        if matchCounter == 0:
            gpio.setLedState(gpio.LED_GREEN, gpio.LED_ON, gpio.ONLY_ONE_LED)
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

    #a = pluginKodi.kodiShowMessage(guess["transcription"])    
    #print(a)
    
    #remove hotword at beginning
    command = guess["transcription"].lower().strip()   
    
    if isinstance(settings.LISTEN_HOTWORD, str):
        settings.LISTEN_HOTWORD = [settings.LISTEN_HOTWORD]
        
    hotword_found = False
    for hotword in sorted(settings.LISTEN_HOTWORD, key=len, reverse = True): #needs to be sorted by string length. Otherwise "Termin" will be replace without "Termine"
        print("Checking for hotword ", hotword, command)     
        (command, n) = re.subn(u"^"+hotword,"", command, flags = re.IGNORECASE) #re.sub seems not to support re.Ignorecase
        if n>0:
            print("Found hotword")
            command = command.strip() 
            hotword_found = True
            break

    print("==========================> Hotword found", hotword_found, "Command >" + command + "<")

    if hotword_found and len(command)==0: #only hotword was detected. => Do not say anything
        print("Hotword detected but no more text came. Aborting")
        return {'result': False, 'message': 'Silence!'}


    if not hotword_found:
        matches = re.findall(u"^(Erz.{0,10}hl[a-z]*|Stell|Gut[a-z]*|Zufallswiedergabe|Unterhalte|Zeig|[Üü]berrasch|Schlaf|Klappe|Halts|Auf|Tschüss|Führ|Schick|Google|Spring|Geh|Geschlafen|Sag|Tages|Extra|Daily|Pause|Stop|Halt|Stop|Spiel|Start|Öffne|Play|Radio|Was|Spule|Mach|Was|Gute)", command, flags = re.IGNORECASE) 
        if not matches:
            print("No hotwords found and also no keywords")
            return {'result': False, 'message': 'Silence!'}
        else:
            print("Keyword not detected but found ", matches)


    a = pluginKodi.kodiShowMessage(guess["transcription"])
    print(a)

    matches = re.findall(u"^(?:Echo).*", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginEcho.echoEcho()
        
    matches = re.findall(u"^Erz.{0,10}hl[a-z]* ein[a-z]* Witz", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginJokes.tellJoke()
        
    matches = re.findall(u"^Goog[a-z]* (?:nach )?(.*)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginBrowser.runGoogleLucky(matches[0])
                
    matches = re.findall(u"^Start[a-z]* dich neu$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginUpdate.restartScript()
            
    matches = re.findall(u"^Start[a-z]* (Kodi|Audi|Pauli) neu$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginUpdate.restartKodi()
        
    matches = re.findall(u"^Start[a-z]* (den |das )?(Raspberry Pi|Raspberry|System|Raspi|Computer) neu$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginUpdate.restartRaspi()
        
    matches = re.findall(u"^([Üü]berrasch[a-z]* mich|Spiel[a-z]* etwas|Spiel[a-z]* was|Zeig[a-z]* mir [a-z]*was|Spiel[a-z]* irgendetwas|Spiel[a-z]* irgendwas|Zufallswiedergabe|Unterhalt[a-z]* mich)$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiSurprise()

    matches = re.findall(u"^(Pause|Break)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPause()

    matches = re.findall(u"^(Stop[a-z]*|Halt[a-z]*|Stop[a-z]*)$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiStop()
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Extra (3|Drei)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Extra 3")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Spiegel.*TV", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Spiegel TV")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Red Bull(.*TV)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Red Bull TV", True)
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )(ein[a-z]* )?Doku(mentation)?", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayDocumentation() 
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )(ein[a-z]* )?zufällig[a-z]* Film?", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRandomMovieByGenre(u"", True, False)
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Maybrit Illner", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Maybrit Illner")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(ein[en]* )?(.{0,2}Live )?(Konzert|Concert)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayFavorites("Concerts")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(ein[en]* )?Talk[ ]*Show", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        pluginKodi.kodiSurpriseTalk()
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Markus Lanz", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Markus Lanz")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(die )?heute Show", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Heute Show")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(ein[en]* |den[ein]* )?Podcast(.*)?", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayPodcast(matches[0][1])

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Youtube(?: mit)? (?:dem|der|den|die|das)?(.*)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube(matches[0])

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(die )?letzt[a-z]* Serie( weiter)?", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayLastTvShow()
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(den )?letzt[a-z]* Film( weiter)?", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayLastMovie()
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(?:ein[a-z]* )?(Komödie|Thriller|Krimi[a-z]*|Liebesfilm|Action[a-z]*|Abenteuer[a-z]*|Animation[a-z]*|Drama|Dokument[a-z]*|Familienfilm|Horror[a-z]*|Kriegsfilm|Mystery[a-z]*|Science-Fiction-Film|Science-Fiction|Western[a-z]*) Trailer", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRandomMovieByGenre(matches[0], False, True)
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?ein[a-z]* (Komödie|Thriller|Krimi[a-z]*|Liebesfilm|Action[a-z]*|Abenteuer[a-z]*|Animation[a-z]*|Drama|Dokument[a-z]*|Familienfilm|Horror[a-z]*|Kriegsfilm|Mystery[a-z]*|Science-Fiction-Film|Science-Fiction|Western[a-z]*)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRandomMovieByGenre(matches[0], False, False)

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(die )?(letzte )?(Tagesschau|Nachrichten)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesschau')
        
    matches = re.findall(u"^(Starte[a-z]* den Tag|Guten Morgen|Was gibt[ e]*s Neues)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesschau')

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(die )?(letzten |letzte )?Tagesthemen", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTagesschau('tagesthemen')

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(?:Radio |Radiosender )?(?:mit )?(SWR[ 0-9]+|RPR[ 0-9]+|Big[ ]*FM|Antenne[ ]*K.*|Deutschland[ ]*funk)", command, flags = re.IGNORECASE)    
    if checkMatch(matches):
        result = pluginKodi.kodiPlayRadio(matches[0])

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(?:die Serie )?(.*) weiter", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayTVShowLastEpisodeByName(matches[0])
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(neu[a-z]*|aktuell[a-z]*) Trailer", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("Neue KINO TRAILER", True)
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?Trailer", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayAvailableMovieTrailers()
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )?(die )?(The )?Daily Show", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayYoutube("The Daily Show")
        
    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )den Film (.*)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayMovie(matches[0])

    matches = re.findall(u"^(?:Play |[a-z]*Spiel[a-z]* |Start[a-z]* |Öffne[a-z]* )(.*)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlayMovieOrSeries(matches[0])

    matches = re.findall(u"^(?:Was läuft|Was läuft gerade|Info|Information)", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiGetCurrentPlaying()

    matches = re.findall(u"^(?:Play|Los|Weiter|Continue|Spiel[a-z]* weiter)[ ]*(den Film)?$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPlay()

    matches = re.findall(u"^(Spring[a-z]* |Geh[a-z]* )?(zu )?(Nächste[a-z]* |Kommend[a-z]* |Folgend[a-z]* )(Film|Folge|Episode)?$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiNext()

    matches = re.findall(u"^(Spring[a-z]* |Geh[a-z]* )?(zu )?(letzter |Letzte |vorherigen |vorigen |vorheriger |vorherige )(Film|Folge|Episode)$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiPrevious()
        
    matches = re.findall(u"^Sag[a-z]* was Nettes( zu mir)?$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = {'result': True, 'message': 'Hallo Lieber Benedikt. Du hast heute sehr sehr lecker gekocht.'}
        
    matches = re.findall(u"^(Wie )?Hat es dir (heute )?geschmeckt$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = {'result': True, 'message': 'Hallo Lieber Benedikt. Es hat mir heute sehr sehr gut geschmeckt.'}
    
    matches = re.findall(u"^(Gut[a-z]* Nacht|Schlaf[a-z]* gut|Geschlafen|Geh[a-z]* schlafen|Auf wiedersehen|Tschüss|Ruhe|Halts maul|Klappe)$", command, flags = re.IGNORECASE)
    if checkMatch(matches): 
        pluginKodi.kodiStop() #ignore result: If already stopped, the result is invalid
        result = pluginSystem.switchTvCec(False)
        result['result']  = False #overwrite result to avoid turn on tv at the end of this function
        
    matches = re.findall(u"^(?:Stell[a-z]* |Setz[a-z]* )Empfindlichkeit auf (.*)$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = settings.setSensitivity(matches[0])
        
    matches = re.findall(u"^(Mach[a-z]* |Führ[a-z]* )ein Update( durch| aus)?$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginUpdate.performUpdate()
        
    matches = re.findall(u"^(?:Schick[a-z]* |Send[a-z]* )?(?:eine )?(?:Mail |Erinnerung |eMail |Erinnere mich )(?:an |mit )?(.*)$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginMail.sendMail(matches[0], "", settings.MAIL_SERVER_SETTINGS_FILE)
        
    matches = re.findall(u"^(Spul[a-z]* |schwul[a-z]* )vor$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiSeek(+30)
        
    matches = re.findall(u"^(Spul[a-z]* |Schwul[a-z]* )zurück$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiSeek(-30)

    matches = re.findall(u"^(?:Mach[a-z]* |Stell[a-z]* )?Leiser$", command, flags = re.IGNORECASE)
    if checkMatch(matches):
        result = pluginKodi.kodiVolumeDown()

    matches = re.findall(u"^(?:Mach[a-z]* |Stell[a-z]* )?Lauter$", command, flags = re.IGNORECASE) 
    if checkMatch(matches):
        result = pluginKodi.kodiVolumeUp()


    if checkResult(result):
        pluginSystem.switchTvCec(True)
    else:
        print("Do not turn on TV since result was not OK", 'result' in result , str(result))

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
    #guess =  {"error": None, "transcription": "Kodi Leiser" }
    #guess =  {"error": None, "transcription": "Termine Stoppe" }
    #guess =  {"error": None, "transcription": u"Kodi Überasch mich" }
    guess =  {"error": None, "transcription": u"Kodi Spiel eine Dokumentation" }
    a = speechInterprete(guess)
    print(a)
