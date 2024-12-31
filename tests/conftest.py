# Content of tests.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import os
import pytest
import paramiko
from amd_desktop.amd64_ping import PingFactory
from unit.amd64_interface import InterfaceFactory
from unit.gitlab import GitLabAPI
from unit.gpio import RaspBerryPins as rbp
from unit.mongodb import MongoDB


MDB_ATTR = [{
    "Log Path": 'logs/uart.log',
    "Report Path": ".report.json"
}]

logging.getLogger("pymongo").setLevel(logging.CRITICAL)
logging.getLogger("amd_desktop.amd64_ping").setLevel(logging.INFO)
logging.getLogger("unit.application_interface").setLevel(logging.INFO)
logging.getLogger("unit.gitlab").setLevel(logging.CRITICAL)
logging.getLogger("unit.gpio").setLevel(logging.INFO)
logging.getLogger("unit.mongodb").setLevel(logging.INFO)
paramiko.util.log_to_file("logs/paramiko.log", level=logging.CRITICAL)

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
        default="wlan0",
        help="Default name of interface: wlan0"
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
    parser.addoption(
        "--workspace",
        action="store",
        default="/home/pi/Projects/AutoRAID/workspace/AutoRAID",
        help="In accordance with the setting in Jenkins"
    )
    parser.addoption(
        "--os_type",
        action="store",
        default="Windows",
        help="Defalt factory OS"
    )
    parser.addoption(
        "--io_file",
        action="store",
        default="D:\\IO.dat",
        help="Defalt IO file"
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
    cmdopt_dic.update(
        {'workspace': request.config.getoption("--workspace")})
    cmdopt_dic.update({'os_type': request.config.getoption("--os_type")})
    cmdopt_dic.update({'io_file': request.config.getoption("--io_file")})
    return cmdopt_dic


@pytest.fixture(scope="session")
def my_pins():
    print('\n\033[32m================= Setup GPIO.2 =================\033[0m')
    return rbp('rpi3_gpio_pins.json', 'GPIO.2')


@pytest.fixture(scope="session", autouse=True)
def store_gitlab_api_in_config(cmdopt, request):
    gitlab_api = GitLabAPI(private_token=cmdopt.get('private_token'),
                           project_id='storage7301426/AutoRAID')
    request.config._store['gitlab_api'] = gitlab_api
    # request.config.cache.set('gitlab_api', gitlab_api)
    # return gitlab_api


@pytest.fixture(scope='session', autouse=True)
def raspi_interface():
    print('\n\033[32m================== Setup RPi Interface =========\033[0m')
    factory = InterfaceFactory()
    return factory.create_interface(
        os_type='Linux',
        mode='local',
        if_name='wlan0',
        ssh_port='22',
        config_file='app_map.json'
    )


@pytest.fixture(scope="session")
def target_ping(raspi_interface):
    print('\n\033[32m================== Setup Ping ==================\033[0m')
    ping = PingFactory()
    return ping.initiate(os_type='Linux', api=raspi_interface)


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
#         logger.info(f'Test case name = \
#           {test_case_name}, ID = {test_case_id}')
#         if test_case_id:
#             if report.failed:
#                 test_result = \
#                   f"Test {test_case_name} failed:\n{report.longrepr}"
#                 label = 'Test Status::Failed'
#                 color = '#FF0000'  # Red
#             if report.skipped:
#                 test_result = \
#                   f"Test {test_case_name} skippeed:\n{report.longrepr}"
#                 label = 'Test Status::Skipped'
#                 color = '#F0AD4E'  # Yellow
#             else:
#                 test_result = f"Test {test_case_name} passed."
#                 label = 'Test Status::Passed'
#                 color = '#00FF00'  # Green
#             note = gitlab_api.push_test_result(test_case_id, test_result,
#                                                label, color)
#             if note:
#                 logger.debug('Successfully pushed test result to GitLab: %s',
#                              note.body)
#                 # Verify if successfully pushed test result
#                 notes = gitlab_api.get_test_case_notes(test_case_id)
#                 latest_note = notes[0] if notes else None
#                 if latest_note and latest_note.body == test_result:
#                     logger.debug('Test result verified in GitLab: %s',
#                                  latest_note.body)
#                 else:
#                     logger.error(
#                       'Failed to verify test result in GitLab for test case '
#                       '%s', test_case_name
#                     )
#             else:
#                 logger.error('Failed to push test result to GitLab for test '
#                   'case %s', test_case_name
#                 )


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
