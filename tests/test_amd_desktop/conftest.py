# Content of test_amd_desktop.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

from amd_desktop.amd64_perf import AMD64Perf as amd64perf
from amd_desktop.amd64_nvme import AMD64NVMe as amd64
from amd_desktop.win10_interface import Win10Interface as win10
from unit.application_interface import ApplicationInterface as api
from unit.mongodb import MongoDB as mdb
from unit.system_under_testing import RaspberryPi as rpi

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger('unit.application_interface').setLevel(logging.DEBUG)
logging.getLogger('amd_desktop.amd64_nvme').setLevel(logging.DEBUG)
logging.getLogger('amd_desktop.win10_interface').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.amd64_perf').setLevel(logging.DEBUG)
logging.getLogger('amd_desktop.amd64_ping').setLevel(logging.INFO)
logging.getLogger('amd_desktop.amd64_stress').setLevel(logging.INFO)
logging.getLogger('unit.mongodb').setLevel(logging.DEBUG)

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)

# @pytest.fixture(scope="session", autouse=True)
# def target_system():
#     print('\n\033[32m================ Setup Platform ===============\033[0m')
#     # return amd64('VEN_1B4B', 'Ethernet 7')
#     # return amd64('')
#     return amd64(my_win10, 'VEN_1B4B')

@pytest.fixture(scope="session", autouse=True)
def my_win10(cmdopt):
    print('\n\033[32m================ Setup Interface ==============\033[0m')
    return win10(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))

@pytest.fixture(scope="session", autouse=True)
def target_system(my_win10):
    print('\n\033[32m================ Setup Platform ===============\033[0m')
    # return amd64('VEN_1B4B', 'Ethernet 7')
    # return amd64(interface=my_win10, str_manufacturer='VEN_1B4B')
    return amd64(interface=my_win10)

@pytest.fixture(scope="session", autouse=True)
def my_mdb():
    print('\n\033[32m================== Setup MongoDB ===============\033[0m')
    return mdb(host='192.168.0.128', port=27017, db_name='AutoRAID',
               collection_name='amd_desktop')

@pytest.fixture(scope="session", autouse=True)
def drone():
    print('\n\033[32m================== Setup RSBPi =================\033[0m')
    return rpi(str_uart_path="/dev/ttyUSB0", int_baut_rate=115200,
               str_file_name="uart.log")

@pytest.fixture(scope="module", autouse=True)
def test_open_uart(drone):
    print('\n\033[32m================== Setup UART ==================\033[0m')
    yield drone.open_uart()
    print('\n\033[32m================ Teardown UART =================\033[0m')
    drone.close_uart()

@pytest.fixture(scope="function", autouse=True)
def target_perf(target_system):
    print('\n\033[32m================ Setup Performance =============\033[0m')
    return amd64perf(platform=target_system, io_file='D:\\IO.dat')

@pytest.fixture(scope="session", autouse=True)
def my_app(cmdopt):
    print('\n\033[32m================== Setup API =================\033[0m')
    return api(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))