# Content of tests/test_arm/conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
# import logging
import pytest
import RPi.GPIO as gpio
from system.arm import RaspberryPi
from unit.gpio import OperateGPIO


@pytest.fixture(scope="module")
def rpi_gpio(my_pins):
    '''This is a docstring'''
    print('\n================== Setup Relay ================================')
    amd_mgi = OperateGPIO(my_pins, gpio.BOARD)

    yield amd_mgi
    print('\n================== Teardown Relay =============================')

    # Clear GPIO
    amd_mgi.clear_gpio()


@pytest.fixture(scope="module")
def drone(raspi_interface):
    """
    Fixture to set up a Raspberry Pi (presumably for drone control).

    Initializes an `Raspberry` object (presumably for interacting with a
    Raspberry Pi) with the specified UART parameters and drone API. This
    fixture has a "session" scope, meaning it will be executed only once per
    test session.

    Args:
        drone_api: The API object for interacting with the drone.

    Returns:
        RaspberryPi: The Raspberry Pi interaction object.
    """
    print("\n\033[32m================== Setup RPi System ============\033[0m")
    return RaspberryPi(
        uart_path='/dev/ttyUSB0',
        baud_rate=115200,
        file_name='logs/uart.log',
        rpi_api=raspi_interface,
    )
