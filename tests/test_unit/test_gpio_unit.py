# Contents of tests/test_unit/test_gpio_unit.py
'''Unit tests for OperateGPIO class, which interacts with RPi.GPIO
   for controlling GPIO pins on a Raspberry Pi. Tests include basic
   GPIO operations like setting up and controlling the power button.

   Copyright (c) 2024 Jaron Cheng
'''
from unittest.mock import MagicMock
import pytest
import RPi.GPIO as gpio
from unit.gpio import OperateGPIO as og


class TestOperateGPIO:
    """Test suite for the OperateGPIO class, which is used for interacting
    with GPIO pins on a Raspberry Pi. This class verifies GPIO setup, power
    button press, and hold functionalities.
    """
    @pytest.fixture(scope="class", autouse=True)
    def setup_gpio(self, my_pins):
        """Fixture to set up the GPIO environment by mocking RPi.GPIO library
        functions, allowing safe tests without actual hardware control.

        Args:
            my_pins (list): List of GPIO pins to be set up for testing.

        Yields:
            OperateGPIO: An instance of OperateGPIO configured with mocked
            pins.
        """
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
        """Tests the press_power_button method of the OperateGPIO class,
        verifying that the GPIO output is set correctly for a press action.

        Args:
            setup_gpio (OperateGPIO): Fixture providing a configured
            OperateGPIO instance.
        """
        setup_gpio.press_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用

    def test_hold_power_button(self, setup_gpio):
        """Tests the hold_power_button method of the OperateGPIO class,
        verifying that the GPIO output is set correctly for a hold action.

        Args:
            setup_gpio (OperateGPIO): Fixture providing a configured
            OperateGPIO instance.
        """
        setup_gpio.hold_power_button()
        gpio.output.assert_called()  # 检查 output 方法是否被调用
