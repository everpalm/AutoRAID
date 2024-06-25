# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
# from amd64_nvme import AMD64NMMe as amd64
from unit.system_under_testing import RasperberryPi as rpi
# from unit.application_interface import ApplicationInterface as api

logger = logging.getLogger(__name__)

def pytest_addoption(parser):
    # For switching local/remote command
    parser.addoption(
        "--mode",
        action="store",
        default="remote",
        help="Default Mode: remote"
    )
    parser.addoption(
        "--if_name",
        action="store",
        default="eth0",
        help="Default name of interface: eth0"
    )
    parser.addoption(
        "--config_file",
        action="store",
        default="app_map.json",
        help="Default config file: app_map.json"
    )


# @pytest.fixture(scope="function")
# @pytest.fixture(scope="module")
@pytest.fixture(scope="session")
def cmdopt(request):
    # return request.config.getoption("--myopt")
    cmdopt_dic = {}
    cmdopt_dic.update({'mode': request.config.getoption("--mode")})
    ''' Apply generate_report.py of lib '''
    cmdopt_dic.update({'if_name': request.config.getoption("--if_name")})
    cmdopt_dic.update({'config_file': request.config.getoption("--config_file")})
    return cmdopt_dic

@pytest.fixture(scope="session", autouse=True)
def drone():
    print('\n\033[32m================ Setup RSBPi ===============\033[0m')
    return rpi("/dev/ttyUSB0", 115200, "uart.log")

@pytest.fixture(scope="session", autouse=True)
def test_open_uart(drone):
    print('\n\033[32m================ Setup UART ===============\033[0m')
    yield drone.open_uart()
    print('\n\033[32m================ Teardown UART ===============\033[0m')
    drone.close_uart()