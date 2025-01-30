echo .
echo Uploading all source to RPi Pico-w 6...
echo .
mkdir /pyboard/src
cp board.py /pyboard
cp boot_wifi.py /pyboard/boot.py
cp main.py /pyboard/main.py
cp main.led /pyboard
cp LICENSE /pyboard
cp led6.conf /pyboard/led.conf
git rev-parse HEAD > version.txt
cp version.txt /pyboard
rsync lib /pyboard/lib
# rsync src /pyboard/src
cp src/configuration.py /pyboard/src
cp src/theapp6w.py pyboard/src/theapp.py
