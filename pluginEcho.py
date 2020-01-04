import settings
from pydub import AudioSegment
from pydub.playback import play##

def echoStoreWav(audio=None):
    try:
        if settings.LISTEN_WRITEWAV is not None and len(settings.LISTEN_WRITEWAV)>0:
                       
            if audio is not None:
                wavdata = audio.get_wav_data()
                f = open(settings.LISTEN_WRITEWAV, 'wb')
                f.write(wavdata)
                f.close()
            else:
                raise Exception("Keine Audio Daten vorhanden")
        else:
            raise Exception("Keine wav-Datei zur Speicherung angegeben.")
    except Exception as e:
        return {'result': False, 'message': 'Kann echo nicht speichern. Grund: '+ str(e)}
    return {'result': True, 'message': 'Audio gespeichert'}


def echoPlayWav():
    try:
        song = AudioSegment.from_wav(settings.LISTEN_WRITEWAV)
        print("Playing recorded file")
        play(song)
    except Exception as e:
        return {'result': False, 'message': 'Kann echo nicht wiedergeben. Grund: '+ str(e)}
    return {'result': True, 'message': 'Audio wurde abgespielt'}
    
def echoEcho():
    result = echoStoreWav()
    if result['result']:
        result = echoPlayWav()
        if result['result']:
            return {'result': True, 'message': 'Silence!'} #no voice output at the end of the command
    return result    