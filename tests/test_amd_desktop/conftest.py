# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
import paramiko
from amd_desktop.amd64_nvme import AMD64NVMe as amd64
from amd_desktop.win10_interface import Win10Interface as win10
from unit.mongodb import MongoDB as mdb
from amd_desktop.amd64_perf import AMD64Perf as amd64perf

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.CRITICAL)
# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('amd_desktop.amd64_nvme').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.win10_interface').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.amd64_perf').setLevel(logging.CRITICAL)
logging.getLogger('amd_desktop.amd64_ping').setLevel(logging.CRITICAL)
# logging.getLogger('unit.application_interface').setLevel(logging.INFO)
# logging.getLogger("pymongo").setLevel(logging.CRITICAL)

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

@pytest.fixture(scope="function", autouse=True)
def target_perf():
    print('\n\033[32m================ Setup DiskSPD ===============\033[0m')
    return amd64perf('remote', 'eth0', 'VEN_1B4B', 'D:\\IO.dat')