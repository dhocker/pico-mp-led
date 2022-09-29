echo .
echo Uploading all source to RPi Pico 3...
echo .
mkdir /pyboard/src
cp board.py /pyboard
cp boot.py /pyboard
cp main.py /pyboard
cp set_rtc.py /pyboard
cp main.led /pyboard
cp main1.led /pyboard
cp LICENSE /pyboard
cp led3.conf /pyboard/led.conf
git rev-parse HEAD > version.txt
cp version.txt /pyboard
rsync lib /pyboard/lib
rsync src /pyboard/src
