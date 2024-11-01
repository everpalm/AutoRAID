# Content of test_amd_desktop.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

# from amd_desktop.amd64_event import WindowsEvent as we
# from amd_desktop.amd64_event import WindowsEventConfig as wec
from amd_desktop.amd64_nvme import AMD64NVMe as amd64
from amd_desktop.amd64_perf import AMD64Perf as amd64perf
from unit.application_interface import ApplicationInterface as api
from unit.mongodb import MongoDB as mdb
from unit.system_under_testing import RaspberryPi as rpi

logging.getLogger('amd_desktop.amd64_event').setLevel(logging.INFO)
logging.getLogger('amd_desktop.amd64_nvme').setLevel(logging.INFO)
logging.getLogger('amd_desktop.amd64_perf').setLevel(logging.INFO)
logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
logging.getLogger('unit.mongodb').setLevel(logging.CRITICAL)
logging.getLogger('unit.system_under_testing').setLevel(logging.CRITICAL)

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)

@pytest.fixture(scope="session")
def my_app(cmdopt):
    print('\n\033[32m================== Setup API ===================\033[0m')
    return api(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))

@pytest.fixture(scope="session")
def target_system(my_app):
    print('\n\033[32m================== Setup Platform ==============\033[0m')
    return amd64(interface=my_app)

@pytest.fixture(scope="session")
def my_mdb():
    print('\n\033[32m================== Setup MongoDB ===============\033[0m')
    return mdb(host='192.168.0.128', port=27017, db_name='AutoRAID',
               collection_name='amd_desktop')

@pytest.fixture(scope="session")
def drone(drone_api):
    print('\n\033[32m================== Setup RSBPi =================\033[0m')
    return rpi(str_uart_path="/dev/ttyUSB0", int_baut_rate=115200,
               str_file_name="logs/uart.log", rpi_api=drone_api)

@pytest.fixture(scope="module", autouse=True)
def test_open_uart(drone):
    print('\n\033[32m================== Setup UART ==================\033[0m')
    yield drone.open_uart()
    print('\n\033[32m================== Teardown UART ===============\033[0m')
    drone.close_uart()

# @pytest.fixture(scope="module")
# def win_event_config(target_system):
#     print('\n\033[32m================== Setup Win Event =============\033[0m')
#     return wec(platform=target_system, config_file='config/win_events.json')

@pytest.fixture(scope="function")
def target_perf(target_system):
    print('\n\033[32m================== Setup Performance ===========\033[0m')
    return amd64perf(platform=target_system, io_file='D:\\IO.dat')


