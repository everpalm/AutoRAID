# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest

# logging.getLogger("pymongo").setLevel(logging.CRITICAL)
# logging.getLogger('unit.system_under_testing').setLevel(logging.CRITICAL)
# logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
# logging.getLogger('unit.ping').setLevel(logging.CRITICAL)

# logger = logging.getLogger(__name__)
@pytest.fixture(scope="session")
def gitlab_api(request):
    return request.config._store.get('gitlab_api', None)



    


    