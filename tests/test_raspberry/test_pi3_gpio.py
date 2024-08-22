# Contents of test_pi3_gpio.py
import logging
import pytest
from tests.test_amd_desktop.test_amd64_ping import TestAMD64Ping
# import RPi.GPIO as gpio

logger = logging.getLogger(__name__)

class TestPowerOffSUT(object):

    @pytest.mark.dependency(name="ping_loss")
    def test_ping_loss(self, target_ping):
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

    @pytest.mark.dependency(depends=["ping_loss"])
    def test_press_power_button(self, rpi_gpio):
        rpi_gpio.press_power_button()


class TestPowerOnSUT(object):

    @pytest.mark.dependency(name="ping_ok")
    def test_power_on(self, target_ping):
        result = target_ping.ping()
        # 检查返回值是否为True，表示ping成功
        assert result == True

    @pytest.mark.dependency(depends=["ping_ok"])
    def test_press_power_button(self, rpi_gpio):
        rpi_gpio.press_power_button()