echo .
echo Uploading all source to RPi Pico 6 with AHLED support...
echo .
mkdir /pyboard/src
cp board.py /pyboard
# Without wifi enabled
# cp boot_wifi.py /pyboard/boot.py
cp boot.py /pyboard
cp main.py /pyboard
cp set_rtc.py /pyboard
cp main.led /pyboard
cp main1.led /pyboard
cp st_default.led /pyboard
cp fy_halloween2.led /pyboard
cp fy_thanksgiving.led /pyboard
cp fy_christmas.led /pyboard
cp LICENSE /pyboard
cp led6.conf /pyboard/led.conf
shell git rev-parse HEAD > version.txt
cp version.txt /pyboard
rsync lib /pyboard/lib
rsync src /pyboard/src
