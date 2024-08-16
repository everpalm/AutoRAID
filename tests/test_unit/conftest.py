# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
import paramiko
from unittest.mock import patch
from unit.application_interface import ApplicationInterface as api
from unit.mongodb import MongoDB
# from unit.system_under_testing import MyGPIO as mgi
# import RPi.GPIO as gpio

logging.getLogger("pymongo").setLevel(logging.CRITICAL)
logging.getLogger('unit.system_under_testing').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def my_app(cmdopt):
    print('\n\033====================Setup API====================\033[0m')
    return api(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))
                
@pytest.fixture(scope="module")
def mongo_db():
    # Mock MongoDB client
    mock_client = patch('unit.mongodb.MongoClient').start()
    mock_db = mock_client.return_value['test_db']
    mock_collection = mock_db['test_collection']

    # Create instance of MongoDB class
    mongo_db_instance = MongoDB('localhost', 27017, 'test_db', 'test_collection')
    
    yield mongo_db_instance, mock_collection
    
    patch.stopall()

@pytest.fixture(scope="session", autouse=True)
def gitlab_api(request):
    return request.config._store.get('gitlab_api', None)
    
    


    