# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''

import pytest
import logging
# import datetime
# import os
# from amd64_nvme import AMD64NMMe as amd64
from unit.system_under_testing import RasperberryPi as rpi
from unit.gitlab import GitLabAPI as glapi
# from unit.application_interface import ApplicationInterface as api

logger = logging.getLogger(__name__)

def pytest_addoption(parser):
    # For switching local/remote command
    # parser.addini(
    #     "log_dir",
    #     help="log directory",
    #     default="tests/logs"
    # )
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
    # parser.addoption(
    #     "--private_token",
    #     action="store",
    #     default="dummy",
    #     help="Please check your Gitlab PAT"
    # )

# def pytest_configure(config):
#     # 确保日志目录存在
#     log_dir = os.path.join(config.rootdir, "tests", "logs")
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)
    
#     # 生成包含执行日期的日志文件名
#     log_file_name = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
#     log_file_path = os.path.join(log_dir, log_file_name)
    
#     # 配置日志文件
#     logging.basicConfig(
#         filename=log_file_path,
#         level=logging.INFO,
#         format='%(asctime)s %(levelname)s %(message)s',
#     )
#     # 打印日志文件路径，便于确认
#     print(f"Logging to file: {log_file_path}")

# @pytest.fixture(scope="function")
# @pytest.fixture(scope="module")
@pytest.fixture(scope="session")
def cmdopt(request):
    # return request.config.getoption("--myopt")
    cmdopt_dic = {}
    cmdopt_dic.update({'mode': request.config.getoption("--mode")})
    cmdopt_dic.update({'if_name': request.config.getoption("--if_name")})
    cmdopt_dic.update({'config_file': request.config.getoption("--config_file")})
    # cmdopt_dic.update({'private_token': request.config.getoption("--private_token")})
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

@pytest.fixture
def gitlab_api():
    return glapi(
        private_token='fake_token',
        project_id='storage7301426/AutoRAID')
