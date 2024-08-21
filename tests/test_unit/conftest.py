# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
# import RPi.GPIO as gpio

# from unittest.mock import MagicMock
# from unittest.mock import patch
from unit.application_interface import ApplicationInterface as api
# from unit.mongodb import MongoDB
# from unit.gpio import OperateGPIO as og
# from unit.gpio import RaspBerryPins as rbp
# from unit.ping import Ping as ping

logging.getLogger("pymongo").setLevel(logging.CRITICAL)
logging.getLogger('unit.system_under_testing').setLevel(logging.CRITICAL)
logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
logging.getLogger('unit.ping').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def my_app(cmdopt):
    print('\n\033[32m================== Setup API =================\033[0m')
    return api(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))
                
# @pytest.fixture(scope="module")
# def mongo_db():
#     print('\n\033[32m================= Setup MongoDB ================\033[0m')
#     # Mock MongoDB client
#     mock_client = patch('unit.mongodb.MongoClient').start()
#     mock_db = mock_client.return_value['test_db']
#     mock_collection = mock_db['test_collection']

#     # Create instance of MongoDB class
#     mongo_db_instance = MongoDB('localhost', 27017, 'test_db',
#                                 'test_collection')
    
#     yield mongo_db_instance, mock_collection
#     print('\n\033[32m=============== Teardown MongoDB ==============\033[0m')
#     patch.stopall()

@pytest.fixture(scope="session", autouse=True)
def gitlab_api(request):
    return request.config._store.get('gitlab_api', None)

# @pytest.fixture(scope="session", autouse=True)    
# def my_pins():
#     print('\n\033==================Setup GPIO.2==================\033[0m')
#     return rbp('rpi3_gpio_pins.json', 'GPIO.2')

# @pytest.fixture(scope="class", autouse=True)
# def setup_gpio(my_pins):
#     print('\n\033=================Set Board Mode=================\033[0m')
    
#     # Mock behavior of RPi.GPIO
#     gpio.setmode = MagicMock()
#     gpio.setup = MagicMock()
#     gpio.output = MagicMock()
#     gpio.cleanup = MagicMock()

#     my_mgi = og(my_pins, gpio.BOARD)
#     yield my_mgi
#     print('\n\033[32m================Teardown GPIO===============\033[0m')
#     my_mgi.clear_gpio()

#     # Clear GPIO
#     gpio.cleanup.assert_called_once()
    
# @pytest.fixture(scope="module", autouse=True)
# def mock_api():
#     mock = MagicMock()
#     mock.remote_ip = "192.168.0.128"
#     return mock
    


    