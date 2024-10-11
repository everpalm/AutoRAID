import pytest
from unittest.mock import MagicMock
from unit.system_under_testing import SystemUnderTesting


@pytest.fixture(scope="function")
def mock_api(mocker):
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
    # Initialize the SystemUnderTesting object with a mock manufacturer
    return SystemUnderTesting('Marvell')


class TestSystemUnderTesting:

    def test_get_cpu_info(self, target_system, mock_api):
        # Mock the response of 'lscpu' command
        mock_api.return_value = {
            1: "CPU(s): 4",
            4: "Model Name: Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz"
        }

        # Call the method to get CPU info
        cpu_info = target_system._get_cpu_info()

        # Assertions to verify correct CPU info is returned
        assert cpu_info['CPU(s)'] == "4"
        assert cpu_info['Model Name'] == ("Intel(R) Core(TM) i5-7500 CPU @ "
        "3.40GHz")

    def test_get_nvme_device(self, target_system, mock_api):
        # Mock the response of 'nvme list' command
        mock_api.return_value = {
            0: "/dev/nvme0n1 00000000000000000000 Marvell_NVMe_Controller 1"
             " 1.02 TB FW Rev: 10001053"
        }

        # Call the method to get NVMe device info
        nvme_info = target_system._get_nvme_device()

        # Assertions to verify correct NVMe device info is returned
        assert nvme_info['Node'] == "nvme0n1"
        assert nvme_info['SN'] == "00000000000000000000"
        assert nvme_info['Model'] == "Marvell_NVMe_Controller"
        assert nvme_info['Namespace ID'] == "1"
        assert nvme_info['Namespace Usage'] == "1.02 TB"
        assert nvme_info['FW Rev'] == "10001053"

    def test_get_nvme_smart_log(self, target_system, mock_api):
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