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
    TEST_PLAN = json.load(f)


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    yield console.initiate(platform=amd64_system)
    print('\n\033[32m================== Teardown Command Test=========\033[0m')


class TestCLI:
    '''docstring'''
    @pytest.mark.parametrize('test_plan', TEST_PLAN)
    def test_commandline(self, mnv_cli, test_plan):
        '''docstring'''
        result = mnv_cli.interpret(test_plan["Test Case"])
        logger.debug('result = %s', result)
        assert result == test_plan["Expected"]
