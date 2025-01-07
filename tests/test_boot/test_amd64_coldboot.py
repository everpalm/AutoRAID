# Contents of test_amd64_coldboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
# import time
import pytest
import RPi.GPIO as gpio
from tests.test_storage.test_stress import TestOneShotStress as Toss
from tests.test_raspberry.test_pi3_gpio import TestPowerOnSUT
from tests.test_raspberry.test_pi3_gpio import TestPowerOffSUT
from unit.gpio import OperateGPIO as og

logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7


@pytest.fixture(scope="module")
def rpi_gpio(my_pins):
    '''This is a docstring'''
    print('\n================== Setup Relay ================================')
    amd_mgi = og(my_pins, gpio.BOARD)

    yield amd_mgi
    print('\n================== Teardown Relay =============================')

    # Clear GPIO
    amd_mgi.clear_gpio()


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(1)
class TestRelayOff(TestPowerOffSUT):
    '''This is a docstring'''


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(2)
class TestRelayOn(TestPowerOnSUT):
    '''This is a docstring'''


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(3)
class TestWindowsColdBootStress(Toss):
    '''This is a docstring'''
