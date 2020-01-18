try:
    import gpiozero #@UnresolvedImport
    hasGPIO = True    
except Exception as e:
    print("Warning: No GPIO output possible ", str(e))
    print("Not running on raspberry pi?")
    hasGPIO = False

def setLedState(a):
    if hasGPIO:
        led = gpiozero.LED(17)
        if a: 
            led.on()
        else:
            led.off()

