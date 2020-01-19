import time
try:
    import gpiozero #@UnresolvedImport
    hasGPIO = True    
except Exception as e:
    print("Warning: No GPIO output possible ", str(e))
    print("Not running on raspberry pi?")
    hasGPIO = False


pinsLed = [26, 17, 16] #0=red, 1=yellow, 2=green

#some consts
LED_RED = 0 
LED_YELLOW = 1
LED_GREEN = 2
ONLY_ONE_LED = True
ALL_LEDS = -1
LED_OFF = False
LED_ON = True

leds = []

def setLedState(ledID, state, setAllOthersToFalse = False):
    if not hasGPIO:
        return
    global leds
    if setAllOthersToFalse:
        setMultipleLed(-1, False)
        
    if state:
        leds[ledID].on()
    else:
        leds[ledID].off()
            
def setMultipleLed(ledID, state):
    if not hasGPIO:
        return
    if not isinstance(ledID, list):
        if ledID < 0 : 
            ledID = range(len(pinsLed))
        else:
            ledID = [ledID]
    for i in ledID:
        setLedState(i, state)    

def init():
    if not hasGPIO:
        return
    global leds    
    for i in pinsLed:
        leds.append( gpiozero.LED(i) )
        

if __name__ == "__main__":
    print("Start")
    led = init()
    while True:
        setMultipleLed([0, 1, 2], True)        
        time.sleep(1)
        setMultipleLed(-1, False)
        time.sleep(1)
