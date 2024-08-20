import logging
import pytest
from unit.application_interface import ApplicationInterface as api
from amd_desktop.amd64_ping import AMD64Ping as aping

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TestAMD64Ping(object):
    @pytest.fixture(scope="session", autouse=True)
    def drone_api(self):
        return api('local', 'eth0', 'app_map.json')

    @pytest.fixture(scope="session", autouse=True)
    def target_ping(self, drone_api):
        print('\n\033[32m================ Setup Ping ===============\033[0m')
        return aping(drone_api)
    
    def test_ping_amd64(self, target_ping):        
        result = target_ping.ping()

    logger.info(f'ping_instance.sent = {target_ping.sent}')
    logger.info(f'ping_instance.received = {target_ping.received}')
    logger.info(f'ping_instance.lost = {target_ping.lost}')
    logger.info(f'ping_instance.minimum = {target_ping.minimum}')
    logger.info(f'ping_instance.maximum = {target_ping.maximum}')
    logger.info(f'ping_instance.average = {target_ping.average}')
    logger.info(f'ping_instance.deviation = {target_ping.deviation}')

