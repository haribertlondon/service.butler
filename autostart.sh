#run 
# $chmod u+x autostart.sh
# $crontab -e (without SUDO!)
# add 
#    @reboot /home/pi/service.butler/autostart.sh &

#wait for boot

echo "Running autostart script"

echo $(date)

echo "I am sleeping for 30sec..."
sleep 30

echo $(date)

#wait for internet connection
while ! /sbin/ifconfig eth0 | grep 'inet [0-9]*'; do
    sleep 3
done

sleep 5

echo "Found ethernet connection"
echo $(date)


echo "Start kodi"
echo $(date)


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

echo "Start service"
echo $(date)


if pgrep -f [^g].*python.*service.* > /dev/null
then
    echo Service Found
else
    echo Change to Service Dir
    cd /home/pi/service.butler 
    echo Starting Service
    #screen -d -m python3 service.py
    #python3 service.py
    screen bash -c 'cd ~/service.butler/; python3 service.py'
fi

 
