# Contents of test_gpio.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import RPi.GPIO as gpio
# from unit.gpio import OperateGPIO as og
# from unit.gpio import RaspBerryPins as rbp
# from unittest.mock import MagicMock

class TestOperateGPIO(object):
    # @pytest.fixture(scope="module", autouse=True)    
    # def my_pins(self):
    #     print('\n\033==================Setup GPIO.2==================\033[0m')
    #     return rbp('rpi3_gpio_pins.json', 'GPIO.2')

    # @pytest.fixture(scope="function", autouse=True)
    # def setup_gpio(self, my_pins):
    #     print('\n\033=================Set Board Mode=================\033[0m')
        
    #     # 模拟 RPi.GPIO 模块的行为
    #     # gpio.setmode = MagicMock()
    #     # gpio.setup = MagicMock()
    #     # gpio.output = MagicMock()
    #     # gpio.cleanup = MagicMock()

    #     my_mgi = og(my_pins, gpio.BOARD)
    #     yield my_mgi
    #     print('\n\033[32m================Teardown GPIO===============\033[0m')
    #     my_mgi.clear_gpio()

    #     # gpio.cleanup.assert_called_once()

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