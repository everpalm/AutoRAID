# Contents of test_gpio.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import RPi.GPIO as gpio
from unittest.mock import MagicMock
from unit.gpio import OperateGPIO as og
from unit.gpio import RaspBerryPins as rbp

class TestOperateGPIO(object):
    @pytest.fixture(scope="module", autouse=True)    
    def my_pins(self):
        print('\n=====================Setup GPIO.2=====================')
        return rbp('rpi3_gpio_pins.json', 'GPIO.2')

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

    # @pytest.mark.skip(reason="Need isolated SUT")
    def test_press_power_button(self, setup_gpio):
        setup_gpio.press_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用
        # TODO
        # Assert power state

    # @pytest.mark.skip(reason="Need isolated SUT")
    def test_hold_power_button(self, setup_gpio):
        setup_gpio.hold_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用
        # assert 2 == 2
        # Assert power state