# Contents of test_commandline.py
'''Unit tests for commandline class, which includes testing the
   execution of mnv_cli commands to verify commands and system responses

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest

from commandline.mnv_cli import CLIFactory

# Set up logger
logger = logging.getLogger(__name__)


def load_and_sort_json(file_path, key):
    '''docstring'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x[key])
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error loading or sorting file {file_path}: {e}")
        return []


# 定義配置檔案與對應鍵
CONFIG_FILES = {
    "test_cases": ("config/test_commandline.json", "ID"),
    "reset_device": ("config/test_mnv_cli_reset_device.json", "ID"),
    "reset_pcie": ("config/test_mnv_cli_reset_pcie.json", "ID"),
    "reset_power": ("config/test_mnv_cli_reset_power.json", "ID"),
    "file_paths": ("config/test_compare_file.json", None),
    "rebuild": ("config/test_mnv_cli_rebuild.json", "ID")
}

# 動態加載與處理檔案
SORTED_DATA = {
    name: load_and_sort_json(path, key) if key else json.load(open(
        path,
        'r',
        encoding='utf-8'
    ))
    for name, (path, key) in CONFIG_FILES.items()
}


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


class TestCLI:
    '''docstring'''
    @pytest.mark.dependency(name="commandline conformance")
    @pytest.mark.parametrize('test_case', SORTED_DATA["test_cases"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        result = mnv_cli.interpret(test_case["Command"])
        logger.debug('result = %s', result)
        assert result == test_case["Expected"]


class TestCLIResetDevice:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_device"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_device_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_device_result = %s', reset_device_result)
        assert reset_device_result == test_case["Expected"]


class TestCLIResetPCIe:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pcie"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pcie_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pcie_result = %s', reset_pcie_result)
        assert reset_pcie_result == test_case["Expected"]


class TestCLIResetPower:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_power"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_power_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_power_result = %s', reset_power_result)
        assert reset_power_result == test_case["Expected"]


class TestCLISMART:
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


class TestCLIExport:
    '''docstring'''
    @pytest.mark.dependency(depends=["commandline conformance"])
    @pytest.mark.parametrize('test_case', SORTED_DATA["file_paths"])
    def test_compare_file(self, mnv_cli, test_case):
        '''docstring'''
        logger.info('file_path = %s', test_case["Name"])
        result = mnv_cli.compare_file(test_case["Name"])
        assert result, 'The two files are not the same!'


class TestCLIRebuild:
    '''docstring'''
    @pytest.mark.dependency(name="rebuild iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_result = %s', rebuild_result)
        assert rebuild_result == test_case["Expected"]
