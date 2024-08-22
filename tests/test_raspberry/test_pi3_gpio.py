# Contents of test_pi3_gpio.py
import logging
import pytest
from unit.gpio import OperateGPIO as og
import RPi.GPIO as gpio

logger = logging.getLogger(__name__)

class TestPi3OperateGPIO(object):
    @pytest.fixture(scope="module", autouse=True)
    def amd_gpio(self, my_pins):
        print('\n================== Setup Relay ==================')
        amd_mgi = og(my_pins, gpio.BOARD)
        
        yield amd_mgi
        print('\n================== Teardown Relay =====================')

        # Clear GPIO
        amd_mgi.clear_gpio()

    def test_press_power_button(self, amd_gpio):
        amd_gpio.press_power_button()
        
        # Assert power state

    # @pytest.mark.skip(reason="Need isolated SUT")
    # def test_hold_power_button(self, amd_gpio):
    #     amd_gpio.hold_power_button()
   
        # assert 2 == 2
        # Assert power state