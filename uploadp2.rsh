echo .
echo Uploading all source to RPi Pico 2...
echo .
mkdir /pyboard/src
cp board.py /pyboard
cp boot.py /pyboard
cp main.py /pyboard
cp set_rtc.py /pyboard
cp main.led /pyboard
cp main1.led /pyboard
cp fy_halloween2.led /pyboard
cp fy_thanksgiving.led /pyboard
cp fy_christmas.led /pyboard
cp LICENSE /pyboard
cp led2.conf /pyboard/led.conf
cp version.txt /pyboard
rsync lib /pyboard/lib
rsync src /pyboard/src
