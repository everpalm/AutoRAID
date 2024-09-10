# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest

# from unit.application_interface import ApplicationInterface as api

logging.getLogger("pymongo").setLevel(logging.CRITICAL)
logging.getLogger('unit.system_under_testing').setLevel(logging.CRITICAL)
logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
logging.getLogger('unit.ping').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

# @pytest.fixture(scope="session", autouse=True)
# def my_app(cmdopt):
#     print('\n\033[32m================== Setup API =================\033[0m')
#     return api(cmdopt.get('mode'), cmdopt.get('if_name'),
#         cmdopt.get('config_file'))

# @pytest.fixture(scope="session", autouse=True)
@pytest.fixture(scope="session")
def gitlab_api(request):
    return request.config._store.get('gitlab_api', None)

    


    