"""Unit tests for HdmiMatrixController."""
# pylint: disable=missing-docstring,invalid-name,too-many-public-methods,protected-access

import logging
import unittest

import serial

import hdmi_matrix_controller

VALID_PORT = 1
INVALID_PORT = 0
VALID_EDID = hdmi_matrix_controller.EDID_1080I_20
INVALID_EDID = 0

logging.disable(logging.CRITICAL)


class FakeSerialDevice(object):

    def __init__(self):
        self.last_write = ''
        self.response = ''
        self._enable_write_exception = False
        self._enable_read_exception = False

    def set_response(self, response):
        self.response = response

    def enable_write_exception(self):
        self._enable_write_exception = True

    def enable_read_exception(self):
        self._enable_read_exception = True

    def write(self, data):
        if self._enable_write_exception:
            raise serial.SerialException()
        self.last_write = data

    def read(self, _):
        if self._enable_read_exception:
            raise serial.SerialException()
        return self.response


class HdmiMatrixControllerTest(unittest.TestCase):

    def setUp(self):
        self.fake_serial_device = FakeSerialDevice()
        self.controller = hdmi_matrix_controller.HdmiMatrixController(
            self.fake_serial_device)

    @staticmethod
    def _cmd_code(cmd):
        return [ord(x) for x in cmd[2:4]]

    @staticmethod
    def _data(cmd):
        return [ord(x) for x in cmd[4:-1]]

    def _validate_sent_cmd(self, cmd, cmd_code, arg1=None, arg2=None):
        self.assertEqual(hdmi_matrix_controller._CMD_LENGTH, len(cmd))
        self.assertEqual(cmd_code, self._cmd_code(cmd))
        if arg1 is not None:
            self.assertEqual(arg1, self._data(cmd)[0])
        if arg2 is not None:
            self.assertEqual(arg2, self._data(cmd)[2])

    def test_change_port_success(self):
        self.controller.change_port(VALID_PORT, VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_CHANGE_PORT,
                                VALID_PORT, VALID_PORT)

    def test_change_port_invalid_input_port(self):
        with self.assertRaises(ValueError):
            self.controller.change_port(INVALID_PORT, VALID_PORT)

    def test_change_port_invalid_output_port(self):
        with self.assertRaises(ValueError):
            self.controller.change_port(VALID_PORT, INVALID_PORT)

    def test_query_port_success(self):
        expected_port = 1
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_PORT, VALID_PORT, expected_port)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_port(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_PORT,
                                VALID_PORT)
        self.assertEqual(expected_port, result)

    def test_query_port_invalid_port(self):
        with self.assertRaises(ValueError):
            self.controller.query_port(INVALID_PORT)

    def test_set_edid_success(self):
        self.controller.set_edid(VALID_PORT, VALID_EDID)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_SET_EDID,
                                VALID_PORT, VALID_PORT)

    def test_set_edid_invalid_port(self):
        with self.assertRaises(ValueError):
            self.controller.set_edid(INVALID_PORT, VALID_EDID)

    def test_set_edid_invalid_value(self):
        with self.assertRaises(ValueError):
            self.controller.set_edid(VALID_PORT, INVALID_EDID)

    def test_set_edid_to_all_success(self):
        self.controller.set_edid_to_all(VALID_EDID)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_SET_EDID_TO_ALL,
                                VALID_PORT)

    def test_set_edid_to_all_invalid_value(self):
        with self.assertRaises(ValueError):
            self.controller.set_edid_to_all(INVALID_EDID)

    def test_copy_edid_success(self):
        self.controller.copy_edid(VALID_PORT, VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_COPY_EDID,
                                VALID_PORT, VALID_PORT)

    def test_copy_edid_invalid_output_port(self):
        with self.assertRaises(ValueError):
            self.controller.copy_edid(INVALID_PORT, VALID_PORT)

    def test_copy_edid_invalid_input_port(self):
        with self.assertRaises(ValueError):
            self.controller.copy_edid(VALID_PORT, INVALID_PORT)

    def test_copy_edid_to_all_success(self):
        self.controller.copy_edid_to_all(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_COPY_EDID_TO_ALL,
                                VALID_PORT)

    def test_copy_edid_to_all_invalid_port(self):
        with self.assertRaises(ValueError):
            self.controller.copy_edid_to_all(INVALID_PORT)

    def test_query_hdp_success(self):
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_HDP, VALID_PORT, 0)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_hdp(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_HDP,
                                VALID_PORT)
        self.assertTrue(result)

        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_HDP, VALID_PORT, 0xff)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_hdp(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_HDP,
                                VALID_PORT)
        self.assertFalse(result)

    def test_query_hdp_invalid_port(self):
        with self.assertRaises(ValueError):
            self.controller.query_hdp(INVALID_PORT)

    def test_query_status_success(self):
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_STATUS, VALID_PORT, 0)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_status(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_STATUS,
                                VALID_PORT)
        self.assertFalse(result)

        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_STATUS, VALID_PORT, 0xff)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_status(VALID_PORT)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_STATUS,
                                VALID_PORT)
        self.assertTrue(result)

    def test_query_status_invalid_port(self):
        with self.assertRaises(ValueError):
            self.controller.query_status(INVALID_PORT)

    def test_set_beep_success(self):
        self.controller.set_beep(True)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_SET_BEEP,
                                hdmi_matrix_controller._BEEP_ON)
        self.controller.set_beep(False)
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_SET_BEEP,
                                hdmi_matrix_controller._BEEP_OFF)

    def test_query_beep_success(self):
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_BEEP, 0, 0)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_beep()
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_BEEP)
        self.assertTrue(result)

        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_BEEP, 0, 0xff)
        self.fake_serial_device.set_response(fake_response)
        result = self.controller.query_beep()
        cmd = self.fake_serial_device.last_write
        self._validate_sent_cmd(cmd, hdmi_matrix_controller._CMD_QUERY_BEEP)
        self.assertFalse(result)

    def test_send_cmd_error(self):
        self.fake_serial_device.enable_write_exception()
        with self.assertRaises(hdmi_matrix_controller.HdmiMatrixControllerException):
            self.controller.query_beep()

    def test_receive_response_error(self):
        self.fake_serial_device.enable_read_exception()
        with self.assertRaises(hdmi_matrix_controller.HdmiMatrixControllerException):
            self.controller.query_beep()

    def test_receive_response_wrong_length(self):
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_BEEP + [0], 0, 0)
        self.fake_serial_device.set_response(fake_response)
        with self.assertRaises(hdmi_matrix_controller.HdmiMatrixControllerException):
            self.controller.query_beep()

    def test_receive_response_wrong_checksum(self):
        fake_response = hdmi_matrix_controller.HdmiMatrixController._generate_cmd(
            hdmi_matrix_controller._CMD_QUERY_BEEP, 0, 0)
        # Modify checksum
        fake_response = fake_response[:-1] + '\x00'
        self.fake_serial_device.set_response(fake_response)
        with self.assertRaises(hdmi_matrix_controller.HdmiMatrixControllerException):
            self.controller.query_beep()


if __name__ == '__main__':
    unittest.main()
