# Contents of tests/test_commandline/test_mnv_cli_init.py
'''Unit tests for commandline class, which includes testing the
   execution of mnv_cli commands to verify init commands and system responses

   Copyright (c) 2025 Jaron Cheng
'''
import json
import logging
import pytest
from unit.json_handler import load_and_sort_json

# Set up logger
logger = logging.getLogger(__name__)


# def load_and_sort_json(file_path, key):
#     '''docstring'''
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         return sorted(data, key=lambda x: x[key])
#     except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
#         logger.error("Error loading or sorting file %s: %s", file_path, e)
#         return []


# 定義配置檔案與對應鍵
CONFIG_FILES = {
    "init": ("config/test_mnv_cli_init.json", "ID"),
    "init_start": ("config/test_mnv_cli_init_start.json", "ID"),
    "init_stop": ("config/test_mnv_cli_init_stop.json", "ID")
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


@pytest.mark.order(39)
class TestCLIInit:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_result = %s', init_result)
        assert init_result == test_case["Expected"]


@pytest.mark.order(40)
class TestCLIInitStart:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init_start"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_start_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_start_result = %s', init_start_result)
        assert init_start_result == test_case["Expected"]


@pytest.mark.order(41)
class TestCLIInitStop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_stop_result = %s', init_stop_result)
        assert init_stop_result == test_case["Expected"]
