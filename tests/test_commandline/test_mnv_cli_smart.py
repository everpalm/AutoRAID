# Contents of tests/test_commandline/test_mnv_smart.py
'''Unit tests for commandline class, which includes testing the execution of
mnv_cli commands to verify smart commands and system responses

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest
from unit.json_handler import load_and_sort_json

# Set up logger
logger = logging.getLogger(__name__)

# Define configuration and key
CONFIG_FILES = {
    "smart_invalid": ("config/test_mnv_cli_smart_invalid.json", "ID")
}

# Load and process file
SORTED_DATA = {
    name: load_and_sort_json(path, key) if key else json.load(open(
        path,
        'r',
        encoding='utf-8'
    ))
    for name, (path, key) in CONFIG_FILES.items()
}


class TestCLISMART:
    '''Docstring'''
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

        # Iterate through the fields to assert limits
        for field, value in smart_info_fields.items():
            assert limits[field](value), (f"{field.replace('_', ' ').title()} "
                                          f"{value} is out of range!")

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


class TestCLISMARTInvalid:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["smart_invalid"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        smart_invalid_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('smart_invalid_result = %s', smart_invalid_result)
        assert smart_invalid_result == test_case["Expected"]
