# Content of tests/test_device/test_1b4b_2241.py
'''Copyright (c) 2025 Jaron Cheng'''
import pytest

from commandline.mnv_cli import CLIFactory
from device.beidou import ChunghuaFactory


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


@pytest.fixture(scope="module")
def boot_device(network_api, mnv_cli):
    target = ChunghuaFactory(network_api)
    print('\n\033[32m================== Setup Device Test ===========\033[0m')
    return target.initiate(command=mnv_cli)
