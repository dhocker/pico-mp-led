# Learning the Raspberry Pi Pico with MicroPython

## Overview
This project was used to gain familarity with the Pico as an LED string controller. Both non-addressable
and addressable LED strings were used. A natural by-product
of this effort was learning [MicroPython](https://docs.micropython.org/en/latest/index.html).

In addition to the LED strings, a [4x20 LCD display](https://smile.amazon.com/dp/B086VVT4NH/?coliid=I36IUW543VNVII&colid=1P1I71J55A82L&psc=1&ref_=lv_ov_lig_dp_it) 
was used for realtime output from the Pico. If you need output from the Pico when it is not attached
to a host, this will work.
 
## Pin Out Reference
![Pin Out](https://projects-static.raspberrypi.org/projects/getting-started-with-the-pico/48619b569f747a7d0550504b77d37f5599bc4e35/en/images/Pico-R3-Pinout.png)

## LCD Display
I2C is used to talk to the LCD.
The code in [this article](https://how2electronics.com/interfacing-16x2-lcd-display-with-raspberry-pi-pico/) was used as a starting point for building an LCD class.

## Non-addressable LED String
A non-addressable LED string has 4 wires: Vcc, Red, Green, Blue. A color is activated by switching
it to ground. Unlike an addressable LED string, LEDs cannot be changed individually. N-channel MOSFETS are
used to do the switching.

![Circuit](https://cdn.sparkfun.com/assets/learn_tutorials/7/3/1/Arduino_Analog_RGB_LED_Strip_Fritzing_bb.jpg)
The wiring diagram is from [Adafruit hookup guide](https://learn.sparkfun.com/tutorials/non-addressable-rgb-led-strip-hookup-guide/all#modifying-rgb-led-strip).

To achieve brightness levels, the RGB GPIO pins are PWM driven. The RGB values are used to derive
a PWM duty cycle for each color.

## APA102/DotStar Addressable LED String
As the heading suggests, each LED (pixel) of an addressable LED string can be controlled independently.
APA102/DotStar based strings use I2C as the communication protocol. Exactly how the protocol works
is beyond the scope of this project. The easiest was to view the protocol is to see it as sending an array of
color values to the string.

[APA102/DotStar module](https://github.com/mattytrentini/micropython-dotstar). This code was used to drive an APA102 string.

## Tools Used
* PyCharm
* rshell
  * upload.rsh script for copying files to Pico
* MicroPython
* 2x20 LCD panel with PCF8574 I2C front end