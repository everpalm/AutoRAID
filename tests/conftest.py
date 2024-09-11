# Content of tests.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
import os
import paramiko
from unit.gitlab import GitLabAPI as glapi
from unit.mongodb import MongoDB
from unit.gpio import RaspBerryPins as rbp
from unit.application_interface import ApplicationInterface as api
from amd_desktop.amd64_ping import AMD64Ping as aping

MDB_ATTR = [{
    "Log Path": 'logs/uart.log',
    "Report Path": ".report.json"
}]

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logging.getLogger("pymongo").setLevel(logging.CRITICAL)
paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--mode",
        action="store",
        default="remote",
        help="Default Mode: remote"
    )
    parser.addoption(
        "--if_name",
        action="store",
        default="eth0",
        help="Default name of interface: eth0"
    )
    parser.addoption(
        "--config_file",
        action="store",
        default="VEN_1B4B.json",
        help="Default config file: VEN_1B4B.json"
    )
    parser.addoption(
        "--private_token",
        action="store",
        default="xxxxx-xxxx",
        help="Check your GitLab Private Token"
    )
    
@pytest.fixture(scope="session")
def cmdopt(request):
    cmdopt_dic = {}
    cmdopt_dic.update({'mode': request.config.getoption("--mode")})
    cmdopt_dic.update({'if_name': request.config.getoption("--if_name")})
    cmdopt_dic.update(
        {'config_file': request.config.getoption("--config_file")})
    cmdopt_dic.update(
        {'private_token': request.config.getoption("--private_token")})
    return cmdopt_dic

@pytest.fixture(scope="session", autouse=True)    
def my_pins():
    print('\n=====================Setup GPIO.2=====================')
    return rbp('rpi3_gpio_pins.json', 'GPIO.2')

@pytest.fixture(scope="session", autouse=True)
def store_gitlab_api_in_config(cmdopt, request):
    gitlab_api = glapi(private_token=cmdopt.get('private_token'),
                       project_id='storage7301426/AutoRAID')
    request.config._store['gitlab_api'] = gitlab_api
    # request.config.cache.set('gitlab_api', gitlab_api)
    # return gitlab_api

@pytest.fixture(scope="session", autouse=True)
def drone_api():
    return api('local', 'eth0', 'app_map.json')

@pytest.fixture(scope="session", autouse=True)
def target_ping(drone_api):
    print('\n\033[32m================ Setup Ping ===============\033[0m')
    return aping(drone_api)

# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     outcome = yield
#     report = outcome.get_result()
#     print('\n\033[32m================ Hook! ===============\033[0m')

#     if report.when == 'call':
#         gitlab_api = item.config._store.get('gitlab_api', None)
#         if gitlab_api is None:
#             logger.debug("GitLab API not found in item.config._store")
#             return

#         test_case_name = item.name
#         test_case_id = gitlab_api.get_test_case_id(test_case_name)
#         logger.info(f'Test case name = {test_case_name}, ID = {test_case_id}')
#         if test_case_id:
#             if report.failed:
#                 test_result = f"Test {test_case_name} failed:\n{report.longrepr}"
#                 label = 'Test Status::Failed'
#                 color = '#FF0000'  # Red
#             if report.skipped:
#                 test_result = f"Test {test_case_name} skippeed:\n{report.longrepr}"
#                 label = 'Test Status::Skipped'
#                 color = '#F0AD4E'  # Yellow
#             else:
#                 test_result = f"Test {test_case_name} passed."
#                 label = 'Test Status::Passed'
#                 color = '#00FF00'  # Green
#             note = gitlab_api.push_test_result(test_case_id, test_result, label, color)
#             if note:
#                 logger.debug(f'Successfully pushed test result to GitLab: {note.body}')
#                 # Verify if successfully pushed test result
#                 notes = gitlab_api.get_test_case_notes(test_case_id)
#                 latest_note = notes[0] if notes else None
#                 if latest_note and latest_note.body == test_result:
#                     logger.debug(f'Test result verified in GitLab: {latest_note.body}')
#                 else:
#                     logger.error(f'Failed to verify test result in GitLab for test case {test_case_name}')
#             else:
#                 logger.error(f'Failed to push test result to GitLab for test case {test_case_name}')

def pytest_sessionfinish(session, exitstatus):
    for item in session.items:
        test_folder = os.path.basename(os.path.dirname(item.fspath))
        collection_name = test_folder.replace('test_', '')
        mongo = MongoDB('192.168.0.128', 27017, 'AutoRAID', collection_name)
        for attr in MDB_ATTR:
            log_path = attr["Log Path"]
            report_path = attr["Report Path"]
            mongo.write_log_and_report(log_path, report_path)

# def pytest_runtest_teardown(item):
#     test_folder = os.path.basename(os.path.dirname(item.fspath))
#     collection_name = test_folder.replace('test_', '')
#     mongo = MongoDB('192.168.0.128', 27017, 'AutoRAID', collection_name)
#     for attr in MDB_ATTR:
#         log_path = attr["Log Path"]
#         report_path = attr["Report Path"]
#         mongo.write_log_and_report(log_path, report_path)