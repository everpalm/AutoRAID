# Content of test_raspberry.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
import RPi.GPIO as gpio

from unit.gpio import OperateGPIO as og

logging.getLogger('raspberry.pi3_gpio').setLevel(logging.DEBUG)

@pytest.fixture(scope="module", autouse=True)
def rpi_gpio(my_pins):
    print('\n================== Setup Relay ==================')
    amd_mgi = og(my_pins, gpio.BOARD)
    
    yield amd_mgi
    print('\n================== Teardown Relay =====================')

    # Clear GPIO
    amd_mgi.clear_gpio()