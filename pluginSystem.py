import os

def switchTvCec(turnOn):    
    try:
        if turnOn: 
            cmd = "echo 'on 0' | cec-client -s -d 1"
        else:
            cmd = "echo 'standby 0' | cec-client -s -d 1"
        
        print('Running command '+cmd)
        os.system(cmd)
    except:
        return {'result': False, 'message': 'Error in switchTvCec'}
    
    return {'result': True, 'message': 'TV was turned to state: '+str(turnOn)}
        
        
if __name__ == "__main__":
    switchTvCec(True)