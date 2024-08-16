import pytest
import RPi.GPIO as gpio
from unit.gpio import OperateGPIO as og
from unit.gpio import RaspBerryPins as rbp

class TestOperateGPIO(object):
    @pytest.fixture(scope="module", autouse=True)    
    def my_pins(self):
        print('\n\033==================Setup GPIO.2==================\033[0m')
        return rbp('rpi3_gpio_pins.json', 'GPIO.2')

    @pytest.fixture(scope="function", autouse=True)
    def setup_gpio(self, my_pins):
        print('\n\033=================Set Board Mode=================\033[0m')
        my_mgi = og(my_pins, gpio.BOARD)
        yield my_mgi
        print('\n\033[32m================Teardown GPIO===============\033[0m')
        my_mgi.clear_gpio()

    @pytest.mark.skip(reason="Need isolated SUT")
    def test_press_power_button(self, setup_gpio):
        setup_gpio.press_power_button()
        # TODO
        # Assert power state

    @pytest.mark.skip(reason="Need isolated SUT")
    def test_hold_power_button(self, setup_gpio):
        setup_gpio.hold_power_button()
        # assert 2 == 2
        # Assert power state