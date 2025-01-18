# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods
# Contents of test_commandline.test_mnv_cli.py
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
        logger.error("Error loading or sorting file %s: %s", file_path, e)
        return []


# 定義配置檔案與對應鍵
CONFIG_FILES = {
    "version": ("config/test_mnv_cli_version.json", "ID"),
    "reset_device": ("config/test_mnv_cli_reset_device.json", "ID"),
    "reset_pcie": ("config/test_mnv_cli_reset_pcie.json", "ID"),
    "reset_pd1": ("config/test_mnv_cli_reset_pd1.json", "ID"),
    "reset_pd2": ("config/test_mnv_cli_reset_pd2.json", "ID"),
    "reset_power": ("config/test_mnv_cli_reset_power.json", "ID"),
    "file_paths": ("config/test_compare_file.json", None),
    "rebuild": ("config/test_mnv_cli_rebuild.json", "ID"),
    "rebuild_pd1": ("config/test_mnv_cli_rebuild_pd1.json", "ID"),
    "rebuild_pd2": ("config/test_mnv_cli_rebuild_pd2.json", "ID"),
    "rebuild_pd1_stop": ("config/test_mnv_cli_rebuild_pd1_stop.json", "ID"),
    "rebuild_pd2_stop": ("config/test_mnv_cli_rebuild_pd2_stop.json", "ID"),
    "info": ("config/test_mnv_cli_info.json", "ID"),
    "identify": ("config/test_mnv_cli_identify.json", "ID"),
    "mp_start": ("config/test_mnv_cli_mp_start.json", "ID"),
    "mp_stop": ("config/test_mnv_cli_mp_stop.json", "ID"),
    "adapter": ("config/test_mnv_cli_adapter.json", "ID"),
    "log": ("config/test_mnv_cli_log.json", "ID"),
    "bga_on": ("config/test_mnv_cli_bga_on.json", "ID"),
    "bga_off": ("config/test_mnv_cli_bga_off.json", "ID"),
    "bga_high": ("config/test_mnv_cli_bga_high.json", "ID"),
    "bga_low": ("config/test_mnv_cli_bga_low.json", "ID"),
    "bga_medium": ("config/test_mnv_cli_bga_medium.json", "ID"),
    "bga_invalid": ("config/test_mnv_cli_bga_invalid.json", "ID"),
    "event": ("config/test_mnv_cli_event.json", "ID"),
    "debug_error": ("config/test_mnv_cli_debug_error.json", "ID"),
    "debug_normal": ("config/test_mnv_cli_debug_normal.json", "ID"),
    "smart_invalid": ("config/test_mnv_cli_smart_invalid.json", "ID"),
    "oem_data": ("config/test_mnv_cli_oem_data.json", "ID"),
    "led": ("config/test_mnv_cli_led.json", "ID"),
    "passthru": ("config/test_mnv_cli_passthru.json", "ID"),
    "dump_hba": ("config/test_mnv_cli_dump_hba.json", "ID")
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


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


@pytest.mark.order(1)
class TestCLIVersion:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["version"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        version_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('version_result = %s', version_result)
        assert version_result == test_case["Expected"]


@pytest.mark.order(2)
class TestCLIResetDevice:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_device"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_device_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_device_result = %s', reset_device_result)
        assert reset_device_result == test_case["Expected"]


@pytest.mark.order(3)
class TestCLIResetPCIe:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pcie"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pcie_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pcie_result = %s', reset_pcie_result)
        assert reset_pcie_result == test_case["Expected"]


@pytest.mark.order(4)
class TestCLIResetPower:
    '''docstring'''
    @pytest.mark.dependency(name="reset iteration")
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_power"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_power_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_power_result = %s', reset_power_result)
        assert reset_power_result == test_case["Expected"]


@pytest.mark.order(5)
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


@pytest.mark.order(6)
@pytest.mark.dependency(depends=["commandline conformance"])
class TestCLIExport:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["file_paths"])
    def test_compare_file(self, mnv_cli, test_case):
        '''docstring'''
        logger.info('file_path = %s', test_case["Name"])
        result = mnv_cli.compare_file(test_case["Name"])
        assert result, 'The two files are not the same!'


@pytest.mark.order(7)
@pytest.mark.dependency(name="rebuild iteration")
class TestCLIRebuild:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_result = %s', rebuild_result)
        assert rebuild_result == test_case["Expected"]


@pytest.mark.order(8)
@pytest.mark.dependency(name="reset pd1")
class TestCLIResetPD1:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pd1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pd1_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pd1_result = %s', reset_pd1_result)
        assert reset_pd1_result == test_case["Expected"]


@pytest.mark.order(9)
@pytest.mark.dependency(name="reset pd2")
class TestCLIResetPD2:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pd2"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pd2_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pd2_result = %s', reset_pd2_result)
        assert reset_pd2_result == test_case["Expected"]


@pytest.mark.dependency(name="rebuild pd1 stop",
                        depends=["reset pd1", "general stress"])
class TestCLIRebuildPD1Stop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd1_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd1_stop_result = %s', rebuild_pd1_stop_result)
        assert rebuild_pd1_stop_result == test_case["Expected"]


@pytest.mark.dependency(name="rebuild pd2 stop",
                        depends=["reset pd2", "general stress"])
class TestCLIRebuildPD2Stop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd2_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd2_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd2_stop_result = %s', rebuild_pd2_stop_result)
        assert rebuild_pd2_stop_result == test_case["Expected"]


@pytest.mark.dependency(name="rebuild pd1", depends=["rebuild pd1 stop"])
class TestCLIRebuildPD1:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd1_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd1_result = %s', rebuild_pd1_result)
        assert rebuild_pd1_result == test_case["Expected"]


@pytest.mark.dependency(name="rebuild pd2", depends=["reset pd2 stop"])
class TestCLIRebuildPD2:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd2"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd2_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd2_result = %s', rebuild_pd2_result)
        assert rebuild_pd2_result == test_case["Expected"]


@pytest.mark.skip(reason="Volatile")
class TestCLIIdentify:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["identify"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        identify_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('identify_result = %s', identify_result)
        assert identify_result == test_case["Expected"]


@pytest.mark.skip(reason="Volatile")
class TestCLIInfo:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["info"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        info_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('info_result = %s', info_result)
        assert info_result == test_case["Expected"]


@pytest.mark.order(10)
class TestCLIAdapter:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["adapter"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        adapter_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('adapter_result = %s', adapter_result)
        assert adapter_result == test_case["Expected"]


@pytest.mark.order(11)
class TestCLILog:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["log"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        log_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('log_result = %s', log_result)
        assert log_result == test_case["Expected"]


@pytest.mark.order(12)
class TestCLIBGAOff:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_off"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_off_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_off_result = %s', bga_off_result)
        assert bga_off_result == test_case["Expected"]


@pytest.mark.order(13)
class TestCLIBGAOn:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_on"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_on_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_on_result = %s', bga_on_result)
        assert bga_on_result == test_case["Expected"]


@pytest.mark.order(14)
class TestCLIBGAHigh:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_high"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_high_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_high_result = %s', bga_high_result)
        assert bga_high_result == test_case["Expected"]


@pytest.mark.order(15)
class TestCLIBGALow:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_low"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_low_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_low_result = %s', bga_low_result)
        assert bga_low_result == test_case["Expected"]


@pytest.mark.order(16)
class TestCLIBGAMedium:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_medium"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_medium_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_medium_result = %s', bga_medium_result)
        assert bga_medium_result == test_case["Expected"]


@pytest.mark.order(17)
class TestCLIBGAInvalid:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_invalid"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_invalid_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_invalid_result = %s', bga_invalid_result)
        assert bga_invalid_result == test_case["Expected"]


@pytest.mark.order(18)
class TestCLIEvent:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["event"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        event_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('event_result = %s', event_result)
        assert event_result == test_case["Expected"]


@pytest.mark.order(19)
class TestCLIDebugError:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["debug_error"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        debug_error_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('debug_error_result = %s', debug_error_result)
        assert debug_error_result == test_case["Expected"]


@pytest.mark.order(20)
class TestCLIDebugNormal:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["debug_normal"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        debug_normal_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('debug_normal_result = %s', debug_normal_result)
        assert debug_normal_result == test_case["Expected"]


class TestCLISMARTInvalid:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["smart_invalid"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        smart_invalid_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('smart_invalid_result = %s', smart_invalid_result)
        assert smart_invalid_result == test_case["Expected"]


class TestCLIOEMData:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["oem_data"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        oem_data_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('oem_data_result = %s', oem_data_result)
        assert oem_data_result == test_case["Expected"]


class TestCLILED:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["led"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        led_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('led_result = %s', led_result)
        assert led_result == test_case["Expected"]


class TestCLIPassthru:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["passthru"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        passthru_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('passthru_result = %s', passthru_result)
        assert passthru_result == test_case["Expected"]


class TestCLIDumpHBA:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["dump_hba"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        dump_hba_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('dump_hba_result = %s', dump_hba_result)
        assert dump_hba_result == test_case["Expected"]


@pytest.mark.order(21)
class TestCLIMPStart:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["mp_start"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        mp_start_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('mp_start_result = %s', mp_start_result)
        assert mp_start_result == test_case["Expected"]


@pytest.mark.order(22)
class TestCLIMPStop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["mp_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        mp_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('mp_stop_result = %s', mp_stop_result)
        assert mp_stop_result == test_case["Expected"]
