# Contents of tests/test_commandline/test_mnv_cli_reset.py
'''Unit tests for commandline class, which includes testing the execution of
mnv_cli commands to verify reset commands and system responses

   Copyright (c) 2025 Jaron Cheng
'''
import json
import logging
import pytest
from unit.json_handler import load_and_sort_json

# Set up logger
logger = logging.getLogger(__name__)

# 定義配置檔案與對應鍵
CONFIG_FILES = {
    "reset_device": ("config/test_mnv_cli_reset_device.json", "ID"),
    "reset_pcie": ("config/test_mnv_cli_reset_pcie.json", "ID"),
    "reset_power": ("config/test_mnv_cli_reset_power.json", "ID"),
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


@pytest.mark.order(11)
class TestCLIResetDevice:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_device"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_device_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_device_result = %s', reset_device_result)
        assert reset_device_result == test_case["Expected"]


@pytest.mark.skip(reason="Deprecated")
@pytest.mark.order(12)
class TestCLIResetPCIe:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pcie"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pcie_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pcie_result = %s', reset_pcie_result)
        assert reset_pcie_result == test_case["Expected"]


@pytest.mark.order(13)
class TestCLIResetPower:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_power"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_power_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_power_result = %s', reset_power_result)
        assert reset_power_result == test_case["Expected"]
