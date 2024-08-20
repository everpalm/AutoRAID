# Contents of test_gpio.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import RPi.GPIO as gpio
# from unit.gpio import OperateGPIO as og
# from unit.gpio import RaspBerryPins as rbp
# from unittest.mock import MagicMock

class TestOperateGPIO(object):
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