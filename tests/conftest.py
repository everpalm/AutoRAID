'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
from unit.system_under_testing import RasperberryPi as rpi
from unit.gitlab import GitLabAPI as glapi

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
        default="app_map.json",
        help="Default config file: app_map.json"
    )

@pytest.fixture(scope="session")
def cmdopt(request):
    cmdopt_dic = {}
    cmdopt_dic.update({'mode': request.config.getoption("--mode")})
    cmdopt_dic.update({'if_name': request.config.getoption("--if_name")})
    cmdopt_dic.update({'config_file': request.config.getoption("--config_file")})
    return cmdopt_dic

@pytest.fixture(scope="session", autouse=True)
def drone():
    print('\n\033[32m================ Setup RSBPi ===============\033[0m')
    return rpi("/dev/ttyUSB0", 115200, "uart.log")

@pytest.fixture(scope="session", autouse=True)
def test_open_uart(drone):
    print('\n\033[32m================ Setup UART ===============\033[0m')
    yield drone.open_uart()
    print('\n\033[32m================ Teardown UART ===============\033[0m')
    drone.close_uart()

@pytest.fixture(scope="session", autouse=True)
def store_gitlab_api_in_config(request):
    gitlab_api = glapi(private_token='glpat-Mk9a-KSfyufsT1yhPmyz', project_id='storage7301426/AutoRAID')
    request.config._store['gitlab_api'] = gitlab_api
    return gitlab_api

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    print('\n\033[32m================ Hook! ===============\033[0m')

    if report.when == 'call':
        gitlab_api = item.config._store.get('gitlab_api', None)
        if gitlab_api is None:
            return

        test_case_name = item.name
        test_case_id = gitlab_api.get_test_case_id(test_case_name)
        logger.debug(f'Test case name = {test_case_name}, ID = {test_case_id}')
        if test_case_id:
            if report.failed:
                test_result = f"Test {test_case_name} failed:\n{report.longrepr}"
                label = 'test status::failed'
                color = '#FF0000'  # Red
            else:
                test_result = f"Test {test_case_name} passed."
                label = 'test status::passed'
                color = '#00FF00'  # Green
            note = gitlab_api.push_test_result(test_case_id, test_result, label, color)
            if note:
                logger.debug(f'Successfully pushed test result to GitLab: {note.body}')
                # Verify if successfully pushed test result
                notes = gitlab_api.get_test_case_notes(test_case_id)
                latest_note = notes[0] if notes else None
                if latest_note and latest_note.body == test_result:
                    logger.debug(f'Test result verified in GitLab: {latest_note.body}')
                else:
                    logger.error(f'Failed to verify test result in GitLab for test case {test_case_name}')
            else:
                logger.error(f'Failed to push test result to GitLab for test case {test_case_name}')
