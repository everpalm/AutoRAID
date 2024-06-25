# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
# from amd64_nvme import AMD64NMMe as amd64
# from unit.system_under_testing import RasperberryPi as rpi
from unit.application_interface import ApplicationInterface as api

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def my_app(cmdopt):
    print('\n\033====================Setup API====================\033[0m')
    return api(cmdopt.get('mode'),
                cmdopt.get('if_name'),
                cmdopt.get('config_file'))