# Contents of tests/test_commandline/test_mnv_cli.py
'''Unit tests for commandline class, which includes testing the
   execution of mnv_cli commands to verify commands and system responses

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest

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
    "file_paths": ("config/test_compare_file.json", None),
    "info": ("config/test_mnv_cli_info.json", "ID"),
    "identify": ("config/test_mnv_cli_identify.json", "ID"),
    "adapter": ("config/test_mnv_cli_adapter.json", "ID"),
    "log": ("config/test_mnv_cli_log.json", "ID"),
    "event": ("config/test_mnv_cli_event.json", "ID"),
    "debug_error": ("config/test_mnv_cli_debug_error.json", "ID"),
    "debug_normal": ("config/test_mnv_cli_debug_normal.json", "ID"),
    "oem_data": ("config/test_mnv_cli_oem_data.json", "ID"),
    "led": ("config/test_mnv_cli_led.json", "ID"),
    "passthru": ("config/test_mnv_cli_passthru.json", "ID"),
    "dump_hba": ("config/test_mnv_cli_dump_hba.json", "ID"),
    "import": ("config/test_mnv_cli_import.json", "ID")
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


@pytest.mark.skip(reason="Volatile")
class TestCLIAdapter:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["adapter"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        adapter_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('adapter_result = %s', adapter_result)
        assert adapter_result == test_case["Expected"]


@pytest.mark.order(1)
class TestCLIOEMData:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["oem_data"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        oem_data_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('oem_data_result = %s', oem_data_result)
        assert oem_data_result == test_case["Expected"]


@pytest.mark.order(2)
class TestCLIVersion:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["version"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        version_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('version_result = %s', version_result)
        assert version_result == test_case["Expected"]


@pytest.mark.order(3)
@pytest.mark.dependency(name="dump data")
class TestCLIDumpHBA:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["dump_hba"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        dump_hba_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('dump_hba_result = %s', dump_hba_result)
        assert dump_hba_result == test_case["Expected"]


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["dump data"])
class TestCLIExport:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["file_paths"])
    def test_compare_file(self, mnv_cli, test_case):
        '''docstring'''
        logger.info('file_path = %s', test_case["Name"])
        result = mnv_cli.compare_file(test_case["Name"])
        assert result, 'The two files are not the same!'


@pytest.mark.order(5)
class TestCLILog:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["log"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        log_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('log_result = %s', log_result)
        assert log_result == test_case["Expected"]


@pytest.mark.order(6)
class TestCLIEvent:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["event"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        event_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('event_result = %s', event_result)
        assert event_result == test_case["Expected"]


@pytest.mark.order(7)
class TestCLIDebugError:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["debug_error"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        debug_error_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('debug_error_result = %s', debug_error_result)
        assert debug_error_result == test_case["Expected"]


@pytest.mark.order(8)
class TestCLIDebugNormal:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["debug_normal"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        debug_normal_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('debug_normal_result = %s', debug_normal_result)
        assert debug_normal_result == test_case["Expected"]


@pytest.mark.order(9)
class TestCLILED:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["led"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        led_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('led_result = %s', led_result)
        assert led_result == test_case["Expected"]


@pytest.mark.order(10)
class TestCLIPassthru:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["passthru"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        passthru_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('passthru_result = %s', passthru_result)
        assert passthru_result == test_case["Expected"]


@pytest.mark.order(41)
class TestCLIImport:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["import"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        import_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('import_result = %s', import_result)
        assert import_result == test_case["Expected"]
