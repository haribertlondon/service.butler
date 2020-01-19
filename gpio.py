import time
try:
    import gpiozero #@UnresolvedImport
    hasGPIO = True    
except Exception as e:
    print("Warning: No GPIO output possible ", str(e))
    print("Not running on raspberry pi?")
    hasGPIO = False

led1 = None
led2 = None

def setLed1State(a):
    global led1
    if hasGPIO:
        if a:
            led1.on()
        else:
            led1.off()

def setLed2State(a):
    global led2
    if hasGPIO:
        if a: 
            led2.on()
        else:
            led2.off()

def init():
    global led1
    global led2
    led1 = gpiozero.LED(17)
    led2 = gpiozero.LED(26)
    

if __name__ == "__main__":
    print("Start")
    led = init()
    while True:
        setLed1State(True)
        setLed2State(True)
        time.sleep(1)
        setLed1State(False)
        setLed2State(False)
        time.sleep(1)
