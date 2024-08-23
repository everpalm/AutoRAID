# Contents of test_pi3_gpio.py
"""
test_pi3_gpio.py

This module contains tests for verifying the power-on and power-off sequences
of a System Under Test (SUT) using GPIO controls on a Raspberry Pi.

Test cases include:
1. Verifying that the SUT experiences a ping loss when powered off.
2. Ensuring that the SUT powers on correctly via a GPIO-triggered power button
   press.
3. Confirming that the SUT can successfully respond to pings after powering
   on.
"""

import logging
import pytest

logging.getLogger(__name__).setLevel(logging.INFO)
logger = logging.getLogger(__name__)

class TestPowerOffSUT(object):
    """
    Test suite for verifying SUT behavior during power-off sequence.
    
    This class contains tests that ensure the SUT loses network connectivity
    when powered off and can respond to a power-on command via GPIO.
    """

    # @pytest.mark.repeat(1)
    @pytest.mark.dependency(name="ping_loss")
    def test_ping_loss(self, target_ping):
        """
        Test suite for verifying SUT behavior during power-off sequence.
        
        This class contains tests that ensure the SUT loses network
        connectivity

        when powered off and can respond to a power-on command via GPIO.
        """
        result = target_ping.ping()

        logger.info(f'target_ping.sent = {target_ping.sent}')
        logger.info(f'target_ping.received = {target_ping.received}')
        logger.info(f'target_ping.lost = {target_ping.lost}')
        logger.info(f'target_ping.minimum = {target_ping.minimum}')
        logger.info(f'target_ping.maximum = {target_ping.maximum}')
        logger.info(f'target_ping.average = {target_ping.average}')
        logger.info(f'ping_instance.deviation = {target_ping.deviation}')
        
        # 检查返回值是否为False，表示ping失败
        assert result == False
        # 验证解析结果

    # @pytest.mark.repeat(1)
    @pytest.mark.dependency(name="power_on", depends=["ping_loss"])
    def test_press_power_button(self, rpi_gpio):
        """
        Test that the SUT powers on when the power button is pressed via GPIO.

        Args:
            rpi_gpio (object): The GPIO control object used to interact with
                               the Raspberry Pi's GPIO pins.
        """
        rpi_gpio.press_power_button()

    # @pytest.mark.repeat(1)
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.dependency(depends=["ping_loss", "power_on"])
    def test_power_on(self, target_ping):
        """
        Test that the SUT successfully powers on and responds to ping after
        power on.

        Args:
            target_ping (object): The ping object used to send and receive ping
                                  requests.
        
        Asserts:
            The ping result should be True, indicating a successful ping
            response.
        """
        result = target_ping.ping()

        # 检查返回值是否为True，表示ping成功
        assert result == True

class TestPowerOnSUT(object):
    """
    Test suite for verifying SUT behavior during power-on sequence.
    
    This class contains tests that ensure the SUT powers on correctly,
    responds to pings, and can be powered off via GPIO.
    """

    # @pytest.mark.repeat(1)
    @pytest.mark.dependency(name="ping_ok")
    def test_power_on(self, target_ping):
        """
        Test that the SUT successfully powers on and responds to ping.

        Args:
            target_ping (object): The ping object used to send and receive ping
                                  requests.
        
        Asserts:
            The ping result should be True, indicating a successful ping
            response.
        """
        result = target_ping.ping()

        logger.info(f'target_ping.sent = {target_ping.sent}')
        logger.info(f'target_ping.received = {target_ping.received}')
        logger.info(f'target_ping.lost = {target_ping.lost}')
        logger.info(f'target_ping.minimum = {target_ping.minimum}')
        logger.info(f'target_ping.maximum = {target_ping.maximum}')
        logger.info(f'target_ping.average = {target_ping.average}')
        logger.info(f'ping_instance.deviation = {target_ping.deviation}')

        # 检查返回值是否为True，表示ping成功
        assert result == True

    # @pytest.mark.repeat(1)
    @pytest.mark.dependency(name="power_off", depends=["ping_ok"])
    def test_press_power_button(self, rpi_gpio):
        """
        Test that the SUT powers off when the power button is pressed via GPIO.

        Args:
            rpi_gpio (object): The GPIO control object used to interact with
                               the Raspberry Pi's GPIO pins.
        """
        rpi_gpio.press_power_button()

    # @pytest.mark.repeat(1)
    @pytest.mark.flaky(reruns=3, reruns_delay=120)
    @pytest.mark.dependency(depends=["ping_ok", "power_off"])
    def test_ping_loss(self, target_ping):
        """
        Test that the SUT experiences ping loss after power off.

        Args:
            target_ping (object): The ping object used to send and receive ping
                                  requests.
        
        Asserts:
            The ping result should be False, indicating no ping response was
            received.
        """
        result = target_ping.ping()

        # 检查返回值是否为False，表示ping失败
        assert result == False
        # 验证解析结果
