# Contents of test_system_under_testing_unit.py
'''Unit tests for the SystemUnderTesting class. This module includes tests
   for various methods within SystemUnderTesting, verifying system
   functionality and configurations.
    Copyright (c) 2024 Jaron Cheng
'''
import pytest
import logging
from unit.system_under_testing import SystemUnderTesting

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def mock_api(mocker):
    """Fixture that mocks the command_line function used within
    SystemUnderTesting, as well as other internal methods like
    _get_remote_ip to simulate the target system's API behavior.

    Args:
        mocker (pytest_mock): pytest's mocker fixture for mocking functions.

    Returns:
        MagicMock: Mocked command_line function.
    """
    # Mock the command_line function used within SystemUnderTesting
    mock_command_line = mocker.patch('unit.system_under_testing.'
                                     'SystemUnderTesting.command_line')

    # Mock _get_remote_ip and __import_config from application_interface
    mock_remote_ip = mocker.patch('unit.system_under_testing.'
                                  'SystemUnderTesting._get_remote_ip')
    mock_remote_ip.return_value = ('127.0.0.1', 'user', 'password',
                                   '/local/dir', '/remote/dir')

    return mock_command_line


@pytest.fixture(scope="function")
def target_system(mock_api):
    """Fixture that initializes a SystemUnderTesting object with a mock
    manufacturer, making use of the mock_api fixture.

    Args:
        mock_api (MagicMock): Mocked API for simulating command-line actions.

    Returns:
        SystemUnderTesting: An instance with mocked dependencies.
    """
    # Initialize the SystemUnderTesting object with a mock manufacturer
    return SystemUnderTesting('Marvell')


class TestSystemUnderTesting:
    """Test suite for SystemUnderTesting methods related to retrieving
    system information, including CPU, NVMe device details, and NVMe
    SMART logs.
    """
    def test_get_cpu_info(self, target_system, mock_api):
        """Test the get_cpu_info method to verify correct CPU information
        retrieval by simulating an 'lscpu' command response.

        Args:
            target_system (SystemUnderTesting): The testing instance.
            mock_api (MagicMock): Mocked API simulating command outputs.
        """
        # Mock the response of 'lscpu' command
        mock_api.return_value = {
            1: "CPU(s): 4",
            4: "Model Name: Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz"
        }

        # Call the method to get CPU info
        cpu_info = target_system.get_cpu_info()

        # Assertions to verify correct CPU info is returned
        assert cpu_info['CPU(s)'] == "4"
        assert cpu_info['Model Name'] == \
            ("Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz")

    def test_get_nvme_device(self, target_system, mock_api):
        """Test the _get_nvme_device method to verify correct NVMe device
        information retrieval by simulating an 'nvme list' command response.

        Args:
            target_system (SystemUnderTesting): The testing instance.
            mock_api (MagicMock): Mocked API simulating command outputs.
        """
        # Mock the response of 'nvme list' command
        mock_api.return_value = {
            0: ("/dev/nvme0n1 00000000000000000000 Marvell_NVMe_Controller 1 "
                "1.02 TB FW Rev: 10001053")
        }

        # Call the method to get NVMe device info
        nvme_info = target_system.get_nvme_device()

        # Assertions to verify correct NVMe device info is returned
        assert nvme_info['Node'] == "nvme0n1"
        assert nvme_info['SN'] == "00000000000000000000"
        assert nvme_info['Model'] == "Marvell_NVMe_Controller"
        assert nvme_info['Namespace ID'] == "1"
        assert nvme_info['Namespace Usage'] == "1.02 TB"
        assert nvme_info['FW Rev'] == "10001053"

    def test_get_nvme_smart_log(self, target_system, mock_api):
        """Test the _get_nvme_smart_log method to verify correct NVMe SMART
        log information retrieval by simulating an 'nvme smart-log' command
        response.

        Args:
            target_system (SystemUnderTesting): The testing instance.
            mock_api (MagicMock): Mocked API simulating command outputs.
        """
        # Mock the response of 'nvme smart-log' command
        mock_api.return_value = {
            1: "critical_warning: 0",
            2: "test temperature: 80",
            11: "power_cycles: 625",
            13: "unsafe_shutdowns: 624"
        }

        # Call the method to get NVMe SMART log info
        smart_log = target_system._get_nvme_smart_log()

        # Assertions to verify correct SMART log is returned
        assert smart_log['critical_warning'] == 0
        assert smart_log['temperature'] == 80
        assert smart_log['power_cycles'] == 625
        assert smart_log['unsafe_shutdowns'] == 624
