# Contents of test_gpio.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import RPi.GPIO as gpio
from unittest.mock import MagicMock
from unit.gpio import OperateGPIO as og

class TestOperateGPIO(object):
    @pytest.fixture(scope="class", autouse=True)
    def setup_gpio(self, my_pins):
        print('\n=====================Set Board Mode=====================')
    
        # Mock behavior of RPi.GPIO
        gpio.setmode = MagicMock()
        gpio.setup = MagicMock()
        gpio.output = MagicMock()
        gpio.cleanup = MagicMock()

        my_mgi = og(my_pins, gpio.BOARD)
        yield my_mgi
        print('\n=====================Teardown GPIO=====================')
        my_mgi.clear_gpio()

        # Clear GPIO
        gpio.cleanup.assert_called_once()

    def test_press_power_button(self, setup_gpio):
        setup_gpio.press_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用

    def test_hold_power_button(self, setup_gpio):
        setup_gpio.hold_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用