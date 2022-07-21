#
# main.py
# This is the MicroPython bootstrap file for the RPi Pico
# © 2022 by Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#
# Put all of your source in the src directory. Create a theapp.py file
# containing at least a run() function. Your application begins there.
# This bootstrap code will call theapp.run() thus starting your app.
# You can use the rshell rsync command to upload your source code
# to the src directory.
#
# Directory structure as seen by rshell
#
# /pyboard
#   main.py
#   src
#       __init__.py
#       theapp.py
#


import sys
from src.theapp import run


try:
    run()
except Exception as ex:
    print("Unhandled exception caught in main")
    # print(str(ex))
    sys.print_exception(ex)
    # raise ex
