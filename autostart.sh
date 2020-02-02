if pgrep kodi.*bin.* > /dev/null
then
    echo Kodi Found. Not starting
else
    echo Kodi Not Found
    echo Wait For Network
    sleep 12
    echo Now Starting Kodi
    kodi --standalone &
    echo Kodi Started
fi

if pgrep -f [^g].*python.*service.* > /dev/null
then
    echo Service Found
else
    echo Starting Service
    screen -d -m "cd /home/pi/service.butler; python service.py"
    cd /home/pi/service.butler; 
    screen -d -m python3 service.py
    cd /home/pi
fi

 
