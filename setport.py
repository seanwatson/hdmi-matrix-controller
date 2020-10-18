import serial
import sys

import hdmi_matrix_controller

BAUD_RATE = 19200
TIMEOUT = 10

serial_dev = serial.Serial('/dev/ttyUSB1', baudrate=BAUD_RATE, timeout=TIMEOUT)
controller = hdmi_matrix_controller.HdmiMatrixController(serial_dev)

#controller.set_beep(0)
controller.change_port(int(sys.argv[1:][0]), int(sys.argv[1:][1]))
print("Done")
