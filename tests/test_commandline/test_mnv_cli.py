# Contents of test_commandline.py
'''Unit tests for the ApplicationInterface class, which includes testing the
   execution of Windows commands to verify system responses and configurations

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest

from commandline.mnv_cli import CLIFactory

# Set up logger
logger = logging.getLogger(__name__)

with open('config/test_commandline.json', 'r', encoding='utf-8') as f:
    TEST_CASE = json.load(f)
sorted_test_cases = sorted(TEST_CASE, key=lambda x: x["ID"])


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


class TestCLI:
    '''docstring'''
    @pytest.mark.parametrize('test_case', sorted_test_cases)
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        result = mnv_cli.interpret(test_case["Command"])
        logger.debug('result = %s', result)
        assert result == test_case["Expected"]

    @pytest.mark.skip(reason="Deprecated")
    def test_get_controller_smart_info(self, mnv_cli):
        '''docstring'''
        smart_info = mnv_cli.get_controller_smart_info()
        for key, value in smart_info.__dict__.items():
            logger.info("%s = %s", key, value)

        limits = {
            "critical_warning": lambda x: 0x00 <= int(x, 16) <= 0x05,
            "composite_temp": lambda x: int(x) < 70,
            "available_spare": lambda x: int(x) > 10,
            "available_spare_threshold": lambda x: int(x) > 0,  # 可以根據需求調整
            "percentage_used": lambda x: int(x) < 100,
        }

        smart_info_fields = smart_info.__dict__
        for field, value in smart_info_fields.items():
            assert limits[field](value), (f"{field.replace('_', ' ').title()} "
                                          f"{value} is out of range!")

    @pytest.mark.skip(reason="Deprecated")
    def test_get_backend_smart_info(self, mnv_cli):
        '''docstring'''
        smart_info = mnv_cli.get_backend_smart_info(pd_id='1')
        for key, value in smart_info.__dict__.items():
            logger.info("%s = %s", key, value)

        limits = {
            "critical_warning": lambda x: 0x00 <= int(x, 16) <= 0x05,
            "composite_temp": lambda x: int(x) < 70,
            "available_spare": lambda x: int(x) > 10,
            "available_spare_threshold": lambda x: int(x) > 0,  # 可以根據需求調整
            "percentage_used": lambda x: int(x) < 100,
            "data_units_read": lambda x: int(x) >= 0,  # 讀取數據單元必須為非負數
            "data_units_written": lambda x: int(x) >= 0,  # 寫入數據單元必須為非負數
            "host_read_commands": lambda x: int(x) >= 0,  # 主機讀命令必須為非負數
            "host_write_commands": lambda x: int(x) >= 0,  # 主機寫命令必須為非負數
            "controller_busy_time": lambda x: int(x) >= 0,  # 控制器忙碌時間必須為非負數
            "power_cycles": lambda x: int(x) >= 0,  # 上電循環次數必須為非負數
            "power_on_hours": lambda x: int(x) >= 0,  # 開機時間必須為非負數
            "unsafe_shutdowns": lambda x: int(x) >= 0,  # 不安全關機次數必須為非負數
            "media_and_data_integrity_errors": lambda x: int(x) == 0,
            "num_err_log_entries": lambda x: int(x) == 0,  # 錯誤記錄條目應為 0
            "warning_composite_temp_time": lambda x: int(x) >= 0,
            "critical_composite_temp_time": lambda x: int(x) >= 0,
            "tmp_1_transition_count": lambda x: int(x) >= 0,  # 溫度管理區域 1 次數
            "tmp_2_transition_count": lambda x: int(x) >= 0,  # 溫度管理區域 2 次數
            "total_time_for_tmp1": lambda x: int(x) >= 0,  # 溫度管理區域 1 總時間
            "total_time_for_tmp2": lambda x: int(x) >= 0,  # 溫度管理區域 2 總時間
        }

        smart_info_fields = smart_info.__dict__

        # 逐項檢查是否符合 limits 規範
        for field, value in smart_info_fields.items():
            assert limits[field](value), (f"{field.replace('_', ' ').title()} "
                                          f"{value} is out of range!")

    @pytest.mark.skip(reason="Only for case generation")
    def test_export_smart_limits(self, mnv_cli):
        '''docstring'''
        cmd_output = mnv_cli.export_smart_limits(
            'config/test_smart_limits.json')
        print(cmd_output)

    def test_import_limits(self, mnv_cli):
        '''docstring'''
        limits = mnv_cli.import_limits(
            'config/test_smart_limits.json')
        for key, value in limits.items():
            logger.info("%s = %s", key, value)

        assert len(limits) == 21, 'The number of limits is not correct!'

        for key, value in limits.items():
            assert callable(value), f'{key} is not a function!'

    def test_get_backend_smart_info1(self, mnv_cli):
        '''docstring'''
        smart_info = mnv_cli.get_backend_smart_info(pd_id='1')
        for key, value in smart_info.__dict__.items():
            logger.info("%s = %s", key, value)

        limits = mnv_cli.import_limits(
            'config/test_smart_limits.json')

        for field, value in smart_info.__dict__.items():
            assert limits[field](value), (f"{field.replace('_', ' ').title()}"
                                          f" {value} is out of range!")

    def test_get_controller_smart_info1(self, mnv_cli):
        '''docstring'''
        smart_info = mnv_cli.get_controller_smart_info()
        for key, value in smart_info.__dict__.items():
            logger.info("%s = %s", key, value)

        limits = mnv_cli.import_limits(
            'config/test_smart_limits.json')

        for field, value in smart_info.__dict__.items():
            assert limits[field](value), (f"{field.replace('_', ' ').title()}"
                                          f" {value} is out of range!")
