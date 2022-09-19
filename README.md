# Raspberry Pi Pico - MicroPython - LEDs

## Overview
This project started out as effort to gain familiarity with the Pico as an LED string controller. 
Both non-addressable, APA102/DotStar and WS281X/NeoPixel type LED strings were used. 
A natural by-product was learning 
[MicroPython](https://docs.micropython.org/en/latest/index.html).

In addition to the LED strings, a [4x20 LCD display](https://smile.amazon.com/dp/B086VVT4NH/?coliid=I36IUW543VNVII&colid=1P1I71J55A82L&psc=1&ref_=lv_ov_lig_dp_it) 
was used for realtime output from the Pico. If you need output from the Pico when it is not attached
to a host, this will work.
 
## Pico Pin Out Reference
![Pin Out](https://projects-static.raspberrypi.org/projects/getting-started-with-the-pico/48619b569f747a7d0550504b77d37f5599bc4e35/en/images/Pico-R3-Pinout.png)

## LCD Display
I2C is used to talk to the PCF8574T based LCD (a 4x20 display).
The code in [this article](https://how2electronics.com/interfacing-16x2-lcd-display-with-raspberry-pi-pico/) was used as a starting point for building an LCD class.

# LED Strings

## Non-addressable LED String
A non-addressable LED string has 4 wires: Vcc, Red, Green, Blue. A color is activated by switching
it to ground. Unlike an addressable LED string, LEDs cannot be changed individually. N-channel MOSFETS are
used to do the switching.

![Circuit](https://cdn.sparkfun.com/assets/learn_tutorials/7/3/1/Arduino_Analog_RGB_LED_Strip_Fritzing_bb.jpg)
The wiring diagram is from [Adafruit hookup guide](https://learn.sparkfun.com/tutorials/non-addressable-rgb-led-strip-hookup-guide/all#modifying-rgb-led-strip). Note that a Pico is being used where the 
diagram shows a RedBoard.

To achieve brightness levels, the RGB GPIO pins are PWM driven. The RGB values are used to derive
a PWM duty cycle for each color (an RGB value of 0-255 is scaled to 0-65535).

**Note that a non-addressable string is treated as if it is an addressable string with one pixel.**
This allows the script engine to work without any special consideration.

## APA102/DotStar Addressable LED String
As the heading suggests, each LED (pixel) of an addressable LED string can be controlled independently.
APA102/DotStar based strings use I2C as the communication protocol. This is a 4 wire protocol:
5v, GND, CI, DI) where 5v and GND are the power supply, CI is the clock and DI is the data.
Exactly how the protocol works
is a bit beyond the scope of this project. The easiest way to view the protocol is to see it as sending an array
of color values to the string.

[APA102/DotStar module](https://github.com/mattytrentini/micropython-dotstar). This code was used to drive an APA102 string.

### [Wiring Diagram](https://learn.adafruit.com/adafruit-dotstar-leds/power-and-connections)

![Wiring Diagram](https://cdn-learn.adafruit.com/assets/assets/000/063/125/original/led_strips_image-1.png?1538880573)

In this design, a level shifter (the 74AHCT125) is used to shift 3.3v controller logic to 5v DotStar logic.

## WS281X/NeoPixel Addressable LED String
These strings come in 5V and 12V versions. They use 3 wires for Vcc, Gnd and data. The data line is
driven using PWM. The data protocol is similar to the DotStar strings. Bascially, 24 or 32 bits per pixel are sent to the string. Each LED takes its data (24 or 32 bits) and forwards the rest.

Working with these strings is simplified by the fact that the Pico version of MicroPython comes with the
[neopixel module](https://docs.micropython.org/en/latest/library/neopixel.html).

### [Wiring Diagram](https://learn.adafruit.com/adafruit-neopixel-uberguide)
![Wiring Diagram](https://cdn-learn.adafruit.com/assets/assets/000/064/121/medium640/led_strips_raspi_NeoPixel_Level_Shifted_bb.jpg?1540314807)

In this design, a level shifter (the 74AHCT125) is used to shift 3.3v controller logic to 5v NeoPixel logic.

## Porting the [AtHomeLED Script Engine](https://github.com/dhocker/athomeled)
It didn't take long to figure out that the scripting engine from
[my Raspberry Pi LED project](https://github.com/dhocker/athomeled)
could be ported to the Pico. This was accomplished by writing a driver for each of the LED string types.
The Pico has plenty of power to run the script engine.

## Tools Used
* [PyCharm](https://www.jetbrains.com/pycharm/)
* [rshell](https://github.com/dhylands/rshell/tree/pico)
  * upload.rsh script for copying files to Pico
  * Use rsync for updating files on the Pico
* [MicroPython](https://docs.micropython.org/en/latest/index.html)
* [2x20 LCD panel with PCF8574T I2C front end](https://amazon.com/dp/B086VVT4NH/?coliid=I36IUW543VNVII&colid=1P1I71J55A82L&psc=1&ref_=lv_ov_lig_dp_it)
  * [Reference](https://wiki.52pi.com/index.php?title=Z-0235)

## Powering the Pico without a Host

If you want to run the Pico as a standalone controller, you can power the Pico by connecting
your +5v supply directly to Pico pin 39 (VSYS). **If you do this, make sure you don't have a USB connection
to a host.** You can use one or the other power source, but you cannot use both without
adding components to prevent issues between the two supplies (VUSB and VSYS).

When the Pico is powered this way, it will start running as soon as you apply power to VSYS.
That means MicroPython will run boot.py and then main.py. thus starting your code.

## Adding a Real Time Clock
A potential drawback of the Pico is the fact that it does not have a realtime clock. When it starts,
it has no idea of what the current time might be. This problem can be rectified by
adding a relatively inexpensive [realtime clock module](https://smile.amazon.com/dp/B07TVMVDDP/).

This is relatively easy to do. 
See [reference](https://www.iotstarters.com/diy-digital-clock-with-rtc-ds1307-and-raspberry-pi-pico/).

# Configuration File
The main app is controlled by the led.conf file. There are a number of sections within the file
that can be used depending on which LED string type you are using.

## All Strings

<table>
  <tbody>
    <tr style="background:#F2F2F2;">
      <th align="left">Key</th>
      <th align="left">Use</th>
    </tr>
    <tr>
      <td>comment...</td>
      <td>Inline documentation that is ignored by the app.</td>
    </tr>
    <tr>
      <td>log_level</td>
      <td></td>
    </tr>
    <tr>
      <td>log_devices</td>
      <td></td>
    </tr>
    <tr>
      <td>test_time</td>
      <td></td>
    </tr>
    <tr>
      <td>colors</td>
      <td></td>
    </tr>
    <tr>
      <td>hold_time</td>
      <td></td>
    </tr>
    <tr>
      <td>brightness</td>
      <td></td>
    </tr>
    <tr>
      <td>terminate_button_pin</td>
      <td></td>
    </tr>
  </tbody>
</table>


## Non-addressable Strings

## APA102/DotStar Strings

## WS281X/NeoPixel Strings

<table>
  <tbody>
    <tr style="background:#F2F2F2;">
      <th align="left">Key</th>
      <th align="left">Use</th>
    </tr>
    <tr>
      <td>comment...</td>
      <td>Inline documentation that is ignored by the app.</td>
    </tr>
    <tr>
      <td>Driver</td>
      <td>
        <p>Available drivers. Case insensitive.</p>
        <ul>
          <li><b>WS2811</b> or <b>NeoPixels</b> (3-wire PWM protocol). Supports WS281X type strings.</li>
          <li><b>adafruit-circuitpython-neopixel</b> or <b>adafruit_circuitpython_neopixel</b> (3-wire PWM protocol using CircuitPython).
            Supports WS281X type strings.
          </li>
          <li><b>APA102</b> or <b>DotStar</b> (4-wire SPI protocol). Supports APA102 style strings.</li>
          <li><b>circuitpython_dotstarapa102</b>  or <b>cpdotstarapa102</b> (4-wire SPI protocol using CircuitPython). 
          Supports APA102 style strings.</li>
          <li><b>led-emulator</b> or <b>emulator</b> (requires led-emulator (https://github.com/dhocker/led-emulator))</li>
        </ul>  
      </td>
    </tr>
    <tr>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>
