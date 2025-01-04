# Contents of test_commandline.py
'''Unit tests for the ApplicationInterface class, which includes testing the
   execution of Windows commands to verify system responses and configurations

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest

from unit.commandline_interface import CLIFactory

# Set up logger
logger = logging.getLogger(__name__)

with open('config/test_commandline.json', 'r', encoding='utf-8') as f:
    TEST_CASE = json.load(f)
sorted_test_cases = sorted(TEST_CASE, key=lambda x: x["Test ID"])


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

    def test_get_controller_smart_info(self, mnv_cli):
        smart_info = mnv_cli.get_controller_smart_info()
        for key, value in smart_info.__dict__.items():
            logger.info("%s = %s", key, value)
        # logger.info('critical_warning = %s', smart_info.critical_warning)
        # logger.info('composite_temp = %s', smart_info.composite_temp)
        # logger.info('available_spare = %s', smart_info.available_spare)
        # logger.info('available_spare_threshold = %s',
        #             smart_info.available_spare_threshold)
        # logger.debug('percentage_used = %s', smart_info.percentage_used)
        # 定義規則
        limits = {
            "critical_warning": lambda x: 0x00 <= int(x, 16) <= 0x05,
            "composite_temp": lambda x: int(x) < 70,
            "available_spare": lambda x: int(x) > 10,
            "available_spare_threshold": lambda x: int(x) > 0,  # 可以根據需求調整
            "percentage_used": lambda x: int(x) < 100,
        }

        # 驗證每個字段
        assert limits["critical_warning"](smart_info.critical_warning), (
            f"Critical Warning {smart_info.critical_warning} is out of range!"
        )
        assert limits["composite_temp"](smart_info.composite_temp), (
            f"Composite Temperature {smart_info.composite_temp} out of range!"
        )
        assert limits["available_spare"](smart_info.available_spare), (
            f"Available Spare {smart_info.available_spare} is out of range!"
        )
        assert limits["available_spare_threshold"](
            smart_info.available_spare_threshold), (
            f"Available Spare Threshold {smart_info.available_spare_threshold}"
            " is out of range!"
        )
        assert limits["percentage_used"](smart_info.percentage_used), (
            f"Percentage Used {smart_info.percentage_used} is out of range!"
        )

    def test_get_backend_smart_info(self, mnv_cli):
        smart_info = mnv_cli.get_backend_smart_info(pd_id='1')
        for key, value in smart_info.__dict__.items():
            # logger.info(f'{key} = {value}')
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
