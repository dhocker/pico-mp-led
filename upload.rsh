echo .
echo Uploading all source to RPi Pico...
echo .
mkdir /pyboard/src
cp board.py /pyboard
cp boot.py /pyboard
cp main.py /pyboard
cp set_rtc.py /pyboard
cp main.led /pyboard
cp LICENSE /pyboard
cp led.conf /pyboard
git rev-parse HEAD > version.txt
cp version.txt /pyboard
rsync lib /pyboard/lib
rsync src /pyboard/src
