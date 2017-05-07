"""Library for controlling an HMDI matrix device over RS232"""

import logging

import serial

# Command constants.
_CMD_HEADER = [0xa5, 0x5b]
_CMD_CODE_LENGTH = 2
_CMD_DATA_LENGTH = 8
_CMD_LENGTH = len(_CMD_HEADER) + _CMD_CODE_LENGTH + _CMD_DATA_LENGTH + 1
_MIN_PORT_NUMBER = 1
_MAX_PORT_NUMBER = 4

# Command codes.
_CMD_CHANGE_PORT = [0x02, 0x03]
_CMD_QUERY_PORT = [0x02, 0x01]
_CMD_SET_EDID = [0x03, 0x02]
_CMD_SET_EDID_TO_ALL = [0x03, 0x01]
_CMD_COPY_EDID = [0x03, 0x04]
_CMD_COPY_EDID_TO_ALL = [0x03, 0x03]
_CMD_QUERY_HDP = [0x01, 0x05]
_CMD_QUERY_STATUS = [0x01, 0x04]
_CMD_SET_BEEP = [0x06, 0x01]
_CMD_QUERY_BEEP = [0x01, 0x0b]

# Values used for representing beep state.
_BEEP_ON = 0x0f
_BEEP_OFF = 0xf0

# Used in calculating checksums.
_CHECKSUM_BASE = 0x100

# EDID values.
EDID_1080I_20 = 1
EDID_1080I_51 = 2
EDID_1080I_71 = 3
EDID_1080P_20 = 4
EDID_1080P_51 = 5
EDID_1080P_71 = 6
EDID_3D_20 = 7
EDID_3D_51 = 8
EDID_3D_71 = 9
EDID_4K2K_20 = 10
EDID_4K2K_51 = 11
EDID_4K2K_71 = 12
EDID_DVI_1024_768 = 13
EDID_DVI_1920_1080 = 14
EDID_DVI_1920_1200 = 15

_MIN_EDID = EDID_1080I_20
_MAX_EDID = EDID_DVI_1920_1200


class HdmiMatrixControllerException(Exception):
    """Exception type thrown for errors receiving data."""
    pass


class HdmiMatrixController(object):
    """Controls an HDMI matrix device over RS232."""

    def __init__(self, serial_device):
        """Initializer.

        Args:
            serial_device (obj: serial.Serial): An open serial device.
        """
        self._ser = serial_device

    @staticmethod
    def _generate_cmd(cmd_code, arg1=0, arg2=0):
        """Builds a command out of all the pieces of a command.

        Args:
            cmd_code (array): The 2 byte command code.
            arg1 (int): First argument to the command if used.
            arg2 (int): Second argument to the command if used.

        Returns:
            str: A complete command ready to be sent over serial.
        """
        data = [0] * _CMD_DATA_LENGTH
        data[0] = arg1
        data[2] = arg2
        cmd = _CMD_HEADER + cmd_code + data
        HdmiMatrixController._append_checksum(cmd)
        return ''.join(chr(c) for c in cmd)

    @staticmethod
    def _append_checksum(cmd):
        """Calculates the checksum and appends it to the command.

        Args:
            cmd (array): A command buffer without a checksum.
        """
        checksum = _CHECKSUM_BASE - sum(cmd)
        if checksum < 0:
            while checksum < 0:
                checksum += 0xff
            checksum += 1
        cmd.append(checksum)

    @staticmethod
    def _checksum_valid(response_data):
        """Checks whether the checksum is valid on a response buffer.

        Args:
            response_buffer (str): A complete response received from the device.

        Returns:
            bool: True if the checksum is valid, False otherwise.
        """
        checksum = _CHECKSUM_BASE - sum(ord(x) for x in response_data[:-1])
        if checksum < 0:
            while checksum < 0:
                checksum += 0xff
            checksum += 1
        return ord(response_data[-1]) == checksum

    @staticmethod
    def _check_port(port_number):
        """Checks if a port number is valid.

        Args:
            port_number (int): The port number to check.

        Raises:
            ValueError: Port number invalid.
        """
        if port_number < _MIN_PORT_NUMBER or port_number > _MAX_PORT_NUMBER:
            logging.error('Invalid port number: %d.', port_number)
            raise ValueError('Invalid port number.')

    @staticmethod
    def _check_edid_value(value):
        """Checks if an EDID value is valid.

        Args:
            value (int): The EDID value to check.

        Raises:
            ValueError: EDID value invalid.
        """
        if value < _MIN_EDID or value > _MAX_EDID:
            logging.error('Invalid EDID value: %d.', value)
            raise ValueError('Invalid EDID value.')

    def change_port(self, input_port, output_port):
        """Changes the input on a given output port.

        Args:
            input_port (int): The input port number to change to.
            output_port (int): The output port number to change.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
            ValueError: Port number invalid.
        """
        self._check_port(input_port)
        self._check_port(output_port)
        logging.debug('Changing port %d input to %d.', output_port, input_port)
        cmd = self._generate_cmd(_CMD_CHANGE_PORT, input_port, output_port)
        self._send_cmd(cmd)

    def query_port(self, output_port):
        """Queries for the input port being used by a given output port.

        Args:
            output_port (int): The output port to query.

        Returns:
            int: The input port number being used.

        Raises:
            HdmiMatrixControllerException: Serial device error.
            ValueError: Port number invalid.
        """
        self._check_port(output_port)
        logging.debug('Querying input port for %d.', output_port)
        cmd = self._generate_cmd(_CMD_QUERY_PORT, output_port)
        self._send_cmd(cmd)
        response = self._receive_response()
        logging.debug('Input port for %d is port %d.', output_port, ord(response[2]))
        return ord(response[2])

    def set_edid(self, input_port, value):
        """Sets the EDID value for a given input port.

        Args:
            input_port (int): The input port number to change.
            value (int): The EDID value to use on the port.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
            ValueError: Port number or value invalid.
        """
        self._check_port(input_port)
        self._check_edid_value(value)
        logging.debug('Setting EDID value to %d for port %d.', value, input_port)
        cmd = self._generate_cmd(_CMD_SET_EDID, value, input_port)
        self._send_cmd(cmd)

    def set_edid_to_all(self, value):
        """Sets the EDID for all input ports.

        Args:
            value (int): The EDID value to use on the ports.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
            ValueError: EDID value is invalid.
        """
        self._check_edid_value(value)
        logging.debug('Setting EDID value to %d for all ports.', value)
        cmd = self._generate_cmd(_CMD_SET_EDID_TO_ALL, value)
        self._send_cmd(cmd)

    def copy_edid(self, output_port, input_port):
        """Copies the EDID value from an output port to an input port.

        Args:
            output_port (int): The output port number to copy from.
            input_port (int): The input port number to copy to.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
            ValueError: Port number invalid.
        """
        self._check_port(output_port)
        self._check_port(input_port)
        logging.debug('Copying EDID from output port %d to input port %d.',
                      output_port, input_port)
        cmd = self._generate_cmd(_CMD_COPY_EDID, output_port, input_port)
        self._send_cmd(cmd)

    def copy_edid_to_all(self, output_port):
        """Copies the EDID value from an output port to all input ports.

        Args:
            output_port (int): The output port number to copy from.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
            ValueError: Port number invalid.
        """
        self._check_port(output_port)
        logging.debug('Copying EDID from output port %d to all input ports.',
                      output_port)
        cmd = self._generate_cmd(_CMD_COPY_EDID_TO_ALL, output_port)
        self._send_cmd(cmd)

    def query_hdp(self, output_port):
        """Queries for the HDP state of an output port.

        Args:
            output_port (int): The output port to query.

        Returns:
            bool: True if the HPD is high, False if HPD is low.

        Raises:
            HdmiMatrixControllerException: Serial device error.
            ValueError: Port number invalid.
        """
        self._check_port(output_port)
        logging.debug('Querying HDP for port %d.', output_port)
        cmd = self._generate_cmd(_CMD_QUERY_HDP, output_port)
        self._send_cmd(cmd)
        response = self._receive_response()
        logging.debug('HDP for port %d: %s.',
                      output_port,
                      'HIGH' if ord(response[2]) == 0 else 'LOW')
        return ord(response[2]) == 0

    def query_status(self, input_port):
        """Queries if an input port is connected.

        Args:
            input_port (int): The input port to query.

        Returns:
            bool: True if the input is connected, False otherwise.

        Raises:
            HdmiMatrixControllerException: Serial device error.
            ValueError: Port number invalid.
        """
        self._check_port(input_port)
        logging.debug('Querying cable status for port %d.', input_port)
        cmd = self._generate_cmd(_CMD_QUERY_STATUS, input_port)
        self._send_cmd(cmd)
        response = self._receive_response()
        logging.debug('Cable status for port %d: %s.',
                      input_port,
                      'connected' if ord(response[2]) != 0 else 'not connected')
        return ord(response[2]) != 0

    def set_beep(self, enable):
        """Enables or disables beeping.

        Args:
            enable (bool): Set to True to enable beep, False to disable.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
        """
        logging.debug('Turning beep %s.', 'on' if enable else 'off')
        beep_value = _BEEP_ON if enable else _BEEP_OFF
        cmd = self._generate_cmd(_CMD_SET_BEEP, beep_value)
        self._send_cmd(cmd)

    def query_beep(self):
        """Queries for whether the beep is enabled.

        Returns:
            bool: True if the beep is enabled, False otherwise.

        Raises:
            HdmiMatrixControllerException: Serial device error.
        """
        logging.debug('Querying beep status.')
        cmd = self._generate_cmd(_CMD_QUERY_BEEP)
        self._send_cmd(cmd)
        response = self._receive_response()
        logging.debug('Beep is %s.', 'enabled' if ord(response[2]) == 0 else 'disabled')
        return ord(response[2]) == 0

    def _send_cmd(self, cmd):
        """Sends a complete command over serial.

        Args:
            cmd (str): Command to send.

        Raises:
            HdmiMatrixControllerException: Error writing to serial.
        """
        try:
            logging.debug('Sending cmd: %s.',
                          ' '.join(c.encode('hex') for c in cmd))
            self._ser.write(cmd)
        except (serial.SerialException, serial.SerialTimeoutException) as exception:
            logging.error('Error writing to serial: %s', str(exception))
            raise HdmiMatrixControllerException(exception, 'Error writing to serial.')

    def _receive_response(self):
        """Reads and validates a response.

        Returns:
            str: The data section of a response as a string.

        Raises:
            HdmiMatrixControllerException: Error reading response.
        """
        try:
            logging.debug('Attempting to read from serial.')
            response = self._ser.read(_CMD_LENGTH)
        except (serial.SerialException, serial.SerialTimeoutException) as exception:
            logging.error('Error reading from serial: %s', str(exception))
            raise HdmiMatrixControllerException(exception, 'Error reading from serial')
        else:
            if len(response) != _CMD_LENGTH or not self._checksum_valid(response):
                logging.error('Response was invalid: %s.',
                              ' '.join(c.encode('hex') for c in response))
                raise HdmiMatrixControllerException('Did not receive valid response')
            logging.debug('Received response: %s.',
                          ' '.join(c.encode('hex') for c in response))
            return response[len(_CMD_HEADER) + _CMD_CODE_LENGTH:-1]
