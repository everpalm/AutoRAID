# Contents of test_commandline_interface_unit.py
'''Copyright (c) 2025 Jaron Cheng'''
import pytest

from commandline.commandline import CLIFactory
from commandline.commandline import LinuxCLI
from commandline.commandline import WindowsCLI
from unittest.mock import MagicMock, patch


# Mocked BaseOS and API for testing
class MockAPI:
    def __init__(self):
        self.command_line = MagicMock()


class MockBaseOS:
    def __init__(self, os_type):
        self.api = MockAPI()
        self.os_type = os_type


# Test WindowsCLI
@patch('unit.commandline_interface.logger')
def test_windows_cli(logger_mock):
    platform = MockBaseOS(os_type='Windows')
    windows_cli = WindowsCLI(platform)

    platform.api.command_line.original.return_value = \
        "Command executed successfully"
    command = "test_command"
    result = windows_cli.interpret(command)

    assert result == "Command executed successfully"
    platform.api.command_line.original.assert_called_once_with(
        platform.api,
        "mnv_cli.exe test_command"
    )
    logger_mock.debug.assert_called_with('composed_cmd = %s',
                                         'mnv_cli.exe test_command')


# Test LinuxCLI
@patch('unit.commandline_interface.logger')
def test_linux_cli(logger_mock):
    platform = MockBaseOS(os_type='Linux')
    linux_cli = LinuxCLI(platform)

    command = "test_command"
    platform.api.command_line.original.return_value = "Linux command executed"

    result = linux_cli.interpret(command)
    assert result == "Linux command executed"
    platform.api.command_line.original.assert_called_once_with(
        platform.api,
        "mnv_cli test_command"
    )


# Test CLIFactory
@patch('unit.commandline_interface.logger')
def test_cli_factory(logger_mock):
    platform_windows = MockBaseOS(os_type='Windows')
    platform_linux = MockBaseOS(os_type='Linux')

    factory_windows = CLIFactory(platform_windows)
    factory_linux = CLIFactory(platform_linux)

    windows_cli_instance = factory_windows.initiate(platform=platform_windows)
    linux_cli_instance = factory_linux.initiate(platform=platform_linux)

    assert isinstance(windows_cli_instance, WindowsCLI)
    assert isinstance(linux_cli_instance, LinuxCLI)

    # Test unsupported OS
    platform_unsupported = MockBaseOS(os_type='UnsupportedOS')
    factory_unsupported = CLIFactory(platform_unsupported)
    with pytest.raises(ValueError, match="Unsupported OS type: UnsupportedOS"):
        factory_unsupported.initiate(platform=platform_unsupported)


@patch('unit.commandline_interface.logger')
def test_windows_cli_error(logger_mock):
    platform = MockBaseOS(os_type='Windows')
    windows_cli = WindowsCLI(platform)

    platform.api.command_line.original.side_effect = \
        Exception("Test exception")
    command = "test_command"

    with pytest.raises(Exception, match="Test exception"):
        windows_cli.interpret(command)

    logger_mock.error.assert_called_once_with(
        'Error occurred in interpretation: %s',
        "Test exception"
    )
