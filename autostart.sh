#run 
# $chmod u+x autostart.sh
# $crontab -e (without SUDO!)
# add 
#    @reboot /home/pi/service.butler/autostart.sh &

#wait for boot
sleep 20

echo "running rc.local" > /tmp/rc_test.txt
echo $(date) >> /tmp/rc_test.txt

#wait for internet connection
while ! /sbin/ifconfig eth0 | grep 'inet [0-9]*'; do
    sleep 3
done

echo "Found ethernet connection" >> /tmp/rc_test.txt
echo $(date) >> /tmp/rc_test.txt


echo "Start kodi" >> /tmp/rc_test.txt
echo $(date) >> /tmp/rc_test.txt


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

echo "Start service" >> /tmp/rc_test.txt
echo $(date) >> /tmp/rc_test.txt


if pgrep -f [^g].*python.*service.* > /dev/null
then
    echo Service Found
else
    echo Starting Service
    cd /home/pi/service.butler; 
    screen -d -m python3 service.py
fi

 
