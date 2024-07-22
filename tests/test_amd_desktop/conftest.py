# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
import paramiko
from amd_desktop.amd64_nvme import AMD64NMMe as amd64
from amd_desktop.win10_interface import Win10Interface as win10

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.CRITICAL)
# logging.getLogger('amd_desktop.amd64_nvme').setLevel(logging.INFO)
# logging.getLogger('amd_desktop.win10_interface').setLevel(logging.CRITICAL)
logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.CRITICAL)
paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)

@pytest.fixture(scope="session", autouse=True)
def target_system():
    print('\n\033[32m================ Setup AMD64 ===============\033[0m')
    return amd64('NVM')

@pytest.fixture(scope="session", autouse=True)
def my_win10(cmdopt):
    print('\n\033[32m================ Setup Win10 ===============\033[0m')
    return win10(cmdopt.get('mode'), cmdopt.get('if_name'),
    cmdopt.get('config_file'))