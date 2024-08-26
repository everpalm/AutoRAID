# Content of test_amd_desktop.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

from amd_desktop.amd64_perf import AMD64Perf as amd64perf
from amd_desktop.amd64_nvme import AMD64NVMe as amd64
from amd_desktop.win10_interface import Win10Interface as win10
from unit.mongodb import MongoDB as mdb
from unit.system_under_testing import RaspberryPi as rpi

logging.getLogger('amd_desktop.amd64_nvme').setLevel(logging.DEBUG)
logging.getLogger('amd_desktop.win10_interface').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.amd64_perf').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.amd64_ping').setLevel(logging.CRITICAL)

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)

@pytest.fixture(scope="session", autouse=True)
def target_system():
    print('\n\033[32m================ Setup Platform ===============\033[0m')
    return amd64('VEN_1B4B', 'Ethernet 7')

@pytest.fixture(scope="session", autouse=True)
def my_win10(cmdopt):
    print('\n\033[32m================ Setup OS ===============\033[0m')
    # return win10(cmdopt.get('mode'), cmdopt.get('if_name'),
    #     cmdopt.get('config_file'))
    return win10()

@pytest.fixture(scope="session", autouse=True)
def my_mdb():
    print('\n\033[32m================ Setup MongoDB ===============\033[0m')
    return mdb('192.168.0.128', 27017, 'AutoRAID', 'amd_desktop')

@pytest.fixture(scope="session", autouse=True)
def drone():
    print('\n\033[32m================== Setup RSBPi =================\033[0m')
    return rpi("/dev/ttyUSB0", 115200, "uart.log")

@pytest.fixture(scope="class", autouse=True)
def test_open_uart(drone):
    print('\n\033[32m================== Setup UART ==================\033[0m')
    yield drone.open_uart()
    print('\n\033[32m================ Teardown UART =================\033[0m')
#     drone.close_uart()

@pytest.fixture(scope="function", autouse=True)
def target_perf():
    print('\n\033[32m================ Setup DiskSPD ===============\033[0m')
    return amd64perf('remote', 'eth0', 'VEN_1B4B', 'D:\\IO.dat')