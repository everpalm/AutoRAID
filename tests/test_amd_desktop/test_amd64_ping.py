# Contents of test_amd64_ping.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from unit.application_interface import ApplicationInterface as api
from amd_desktop.amd64_ping import AMD64Ping as aping

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)

class TestAMD64Ping(object):
    @pytest.fixture(scope="module", autouse=True)
    def drone_api(self):
        return api('local', 'eth0', 'app_map.json')

    @pytest.fixture(scope="module", autouse=True)
    def target_ping(self, drone_api):
        print('\n\033[32m================ Setup Ping ===============\033[0m')
        return aping(drone_api)
    
    @pytest.mark.flaky(reruns=3, reruns_delay=10)
    # @pytest.mark.xfail(reason="Cannot be used with flaky")
    def test_ping_amd64(self, target_ping):        
        result = target_ping.ping()

        logger.info(f'target_ping.sent = {target_ping.sent}')
        logger.info(f'target_ping.received = {target_ping.received}')
        logger.info(f'target_ping.lost = {target_ping.lost}')
        logger.info(f'target_ping.minimum = {target_ping.minimum}')
        logger.info(f'target_ping.maximum = {target_ping.maximum}')
        logger.info(f'target_ping.average = {target_ping.average}')
        logger.info(f'target_ping.deviation = {target_ping.deviation}')

        assert result == True, "Ping should succeed"
        assert target_ping.sent > 0, "Packets sent should be greater than 0"
        assert target_ping.received > 0, ("Packets received should be greater"
                                          "than 0")
        assert target_ping.lost >= 0, "Packets lost should be 0 or greater"
        assert target_ping.minimum >= 0, "Minimum RTT should be 0 or greater"
        assert target_ping.average >= 0, "Average RTT should be 0 or greater"
        assert target_ping.maximum >= 0, "Maximum RTT should be 0 or greater"
        assert target_ping.deviation >= 0, ("Deviation RTT should be 0 or"
                                            " greater")
        

