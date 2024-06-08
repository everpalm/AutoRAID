# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest


def pytest_addoption(parser):
    # For switching local/remote command
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


# @pytest.fixture(scope="function")
# @pytest.fixture(scope="module")
@pytest.fixture(scope="session")
def cmdopt(request):
    # return request.config.getoption("--myopt")
    cmdopt_dic = {}
    cmdopt_dic.update({'mode': request.config.getoption("--mode")})
    ''' Apply generate_report.py of lib '''
    cmdopt_dic.update({'if_name': request.config.getoption("--if_name")})
    cmdopt_dic.update({'config_file': request.config.getoption("--config_file")})
    return cmdopt_dic
