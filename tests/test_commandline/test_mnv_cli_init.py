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

# Define configuration and key
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


class TestCLIInit:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_result = %s', init_result)
        assert init_result == test_case["Expected"]


class TestCLIInitStart:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init_start"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_start_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_start_result = %s', init_start_result)
        assert init_start_result == test_case["Expected"]


class TestCLIInitStop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["init_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        init_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('init_stop_result = %s', init_stop_result)
        assert init_stop_result == test_case["Expected"]
