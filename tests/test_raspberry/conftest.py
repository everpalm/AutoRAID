# Content of test_raspberry.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
# import logging
import pytest
import RPi.GPIO as gpio

from unit.gpio import OperateGPIO as og

# logging.getLogger('raspberry.pi3_gpio').setLevel(logging.CRITICAL)
# logging.getLogger('unit.ping').setLevel(logging.CRITICAL)


@pytest.fixture(scope="module")
def rpi_gpio(my_pins):
    '''This is a docstring'''
    print('\n================== Setup Relay ================================')
    amd_mgi = og(my_pins, gpio.BOARD)

    yield amd_mgi
    print('\n================== Teardown Relay =============================')

    # Clear GPIO
    amd_mgi.clear_gpio()
