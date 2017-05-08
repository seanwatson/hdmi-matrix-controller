[![Build Status](https://travis-ci.org/seanwatson/hdmi-matrix-controller.svg?branch=master)](https://travis-ci.org/seanwatson/hdmi-matrix-controller)
[![Coverage Status](https://coveralls.io/repos/github/seanwatson/hdmi-matrix-controller/badge.svg?branch=master)](https://coveralls.io/github/seanwatson/hdmi-matrix-controller?branch=master)

Python implementation of the Monoprice Blackbird HDMI Matrix Controller serial protocol.

[Protocol spec](https://www.lindy.co.uk/downloads/1459947591Command_codes_for_LINDY_38152.pdf)

Example usage:

    import serial

    import hdmi_matrix_controller

    BAUD_RATE = 19200
    TIMEOUT = 1

    serial_dev = serial.Serial('/dev/ttyUSB0', BAUD_RATE, TIMEOUT)
    controller = hdmi_matrix_controller.HdmiMatrixController(serial_dev)

    controller.set_beep(false)
    controller.change_port(1, 2)
