#
# From: https://how2electronics.com/interfacing-16x2-lcd-display-with-raspberry-pi-pico/
#

from pico_i2c_lcd import I2cLcd
from machine import I2C
from machine import Pin
import time


def run_lcd_test():

    print("Testing LCD...")

    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
    # i2c = I2C(id=1, scl=Pin(1), sda=Pin(0), freq=400000)
    rows = 4
    cols = 20
    lcd = I2cLcd(i2c, 0x27, rows, cols)

    try:
        hw = "Hello World"
        x = 0
        y = 0
        incr = 1
        for i in range(20):
            lcd.put_str(x, y, hw)
            time.sleep(1.0)
            x += incr
            if x > (rows - 1):
                x = 0
                lcd.clear()
            y = (y + incr) % rows
    except KeyboardInterrupt:
        print("LCD testing interrupted")
    finally:
        lcd.clear()
        lcd.backlight_off()

    print("LCD testing complete")
