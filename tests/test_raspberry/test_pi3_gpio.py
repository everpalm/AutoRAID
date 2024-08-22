# Contents of test_pi3_gpio.py
import logging
import pytest
# from unit.gpio import OperateGPIO as og
# import RPi.GPIO as gpio

logger = logging.getLogger(__name__)

class TestPowerOffSUT(object):
    # @pytest.fixture(scope="module", autouse=True)
    # def amd_gpio(self, my_pins):
    #     print('\n================== Setup Relay ==================')
    #     amd_mgi = og(my_pins, gpio.BOARD)
        
    #     yield amd_mgi
    #     print('\n================== Teardown Relay =====================')

    #     # Clear GPIO
    #     amd_mgi.clear_gpio()
    # @pytest.fixture(scope="module", autouse=True)
    # def drone_api(self):
    #     return api('local', 'eth0', 'app_map.json')

    # @pytest.fixture(scope="module", autouse=True)
    # def target_ping(self, drone_api):
    #     print('\n\033[32m================ Setup Ping ===============\033[0m')
    #     return aping(drone_api)
    
    # def test_sut_power_on(self, target_ping):
    #     bool_power_state = target_ping.ping()
    #     logger.info(f'bool_power_state = {bool_power_state}')
    #     assert bool_power_state == True

    # @pytest.mark.dependency(depends=["test_sut_power_on"])
    def test_press_power_button(self, rpi_gpio):
    # #     # tap.test_ping_amd64()
            rpi_gpio.press_power_button()
        # pass
        
        # Assert power state

    # @pytest.mark.skip(reason="Need isolated SUT")
    # def test_hold_power_button(self, amd_gpio):
    #     amd_gpio.hold_power_button()
   
        # assert 2 == 2
        # Assert power state