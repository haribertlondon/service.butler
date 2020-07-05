import settings
try:
    from pydub import AudioSegment
    import pydub.playback 
    import playsound
except:
    pass
import time
import os

def removeOldFiles(fileNamePart, path, maxLen):
    try:
        full = os.listdir(path)
        #print("-----full----")
        #print(full)
        lst = []
        for item in full:
            if fileNamePart in item and ".wav" in item:
                lst.append(item)
        lst = sorted(lst)
        #print("-----lst----")
        #print(lst)
        
        maxN = len(lst)-maxLen
        if maxN>0:
            lst = lst[:maxN]
            for item in lst:
                print("Deleting wav file: ", item)
                os.remove(item)
        else:
            print("Only "+str(len(lst))+" files found. Nothing must be deleted.")
    except Exception as e:
        print("Error in CycleWav: Remove Old Files ", e)
    

def echoStoreWavCycleBuffer(audio=None, fileNamePart="cycle_", path = "./", maxLen = 20, response=None):
    removeOldFiles(fileNamePart, path, maxLen)
    fileName = os.path.join(path , fileNamePart+time.strftime("%Y_%m_%d-%H_%M_%S")+".wav")
    
    result = echoStoreWav(audio, fileName, response)        
    print(result)
    return result

def echoStoreWav(audio=None, fileName = None, response = None):
    try:
        if fileName is None: 
            fileName = settings.LISTEN_WRITEWAV
            
        print("Store audio data as wav: ",fileName)
             
        if fileName is not None and len(fileName)>0:
            if audio is not None:
                wavdata = audio.get_wav_data()
                f = open(fileName, 'wb')
                f.write(wavdata)
                f.close()
            else:
                raise Exception("Keine Audio Daten vorhanden")
        else:
            raise Exception("Keine wav-Datei zur Speicherung angegeben.")
        
        if response is not None:
            filenameTxt = fileName.replace(".wav",".txt") 
            text_file = open(filenameTxt, "w")
            text_file.write(str(response))
            text_file.close()
            
    except Exception as e:
        print("Exception in echoStoreWav", e)
        return {'result': False, 'message': 'Kann echo nicht speichern. Grund: '+ str(e)}
    return {'result': True, 'message': 'Audio gespeichert'}


def echoPlay(fileName = None, volume=None):
    
    if fileName is None:
        fileName = settings.LISTEN_WRITEWAV
    if volume is None:
        volume = settings.OUTPUT_VOLUME_DB
    
    try:        
        if ".wav" in fileName:
            song = AudioSegment.from_wav(fileName)
        elif ".mp3" in fileName:
            song = AudioSegment.from_mp3(fileName)
        print("Current volume: ", song.dBFS)
        change_in_dBFS = volume - song.dBFS
        song = song.apply_gain(change_in_dBFS)
        print("Current volume: ", song.dBFS)
        print("Playing recorded file")
        pydub.playback.play(song)
    except Exception as e:
        print("Failed to play "+str(e)+". Now using Fallback without volume control")
        try:
            playsound.playsound(fileName)
        except Exception as e:
            print(e)
            return {'result': False, 'message': 'Kann echo nicht wiedergeben. Grund: '+ str(e)}
    return {'result': True, 'message': 'Audio wurde abgespielt'}
    
def echoEcho():
    result = echoStoreWav()
    if result['result']:
        result = echoPlay()
        if result['result']:
            return {'result': True, 'message': 'Silence!'} #no voice output at the end of the command
    return result    

if __name__ == "__main__":   
    echoPlay()
