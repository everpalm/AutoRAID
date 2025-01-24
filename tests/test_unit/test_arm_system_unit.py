import pytest
from unittest.mock import MagicMock
from arm.system import RaspberryPi
from unittest.mock import patch


@pytest.fixture
def mock_rpi():
    """Fixture to set up RaspberryPi instance with mocked API."""
    mock_api = MagicMock()
    uart_path = "/dev/ttyAMA0"
    baud_rate = 115200
    file_name = "uart_log.txt"
    return RaspberryPi(uart_path, baud_rate, file_name, mock_api), mock_api


def test_get_memory_size_success(mock_rpi):
    rpi, mock_api = mock_rpi
    print('rpi = ', rpi)
    print('mock_api = ', mock_api)
    mock_api.command_line.original.return_value = \
        ["MemTotal:       1024000 kB"]
    value, unit = rpi._get_memory_size()

    print('value = ', value)
    print('unit = ', unit)
    assert value == 1024000
    assert unit == "kB"
    mock_api.command_line.original.assert_called_with(
        mock_api, "cat /proc/meminfo | grep MemTotal"
    )


def test_get_memory_size_failure_with_mock_logger(mock_rpi):
    rpi, mock_api = mock_rpi

    # 模擬 API 拋出異常
    mock_api.command_line.original.side_effect = Exception("Command failed")

    # 使用 patch 模擬 logger
    with patch("arm.system.logger.error") as mock_error_logger:
        with pytest.raises(Exception, match="Command failed"):
            rpi._get_memory_size()

        # 驗證 logger.error 被正確調用
        mock_error_logger.assert_called_once_with(
            "Failed to retrieve memory size: %s", "Command failed"
        )


def test_get_cpu_info_success(mock_rpi):
    rpi, mock_api = mock_rpi
    mock_api.command_line.original.return_value = ["Model\t: Raspberry Pi 4"]

    model_name = rpi.get_cpu_info()

    assert model_name == "Raspberry Pi 4"
    mock_api.command_line.original.assert_called_with(
        mock_api, "cat /proc/cpuinfo | grep 'Model'"
    )


def test_get_cpu_info_failure_with_mock_logger(mock_rpi):
    rpi, mock_api = mock_rpi

    # 模擬 API 拋出異常
    mock_api.command_line.original.side_effect = Exception("Command failed")

    # 使用 patch 模擬 logger
    with patch("arm.system.logger.error") as mock_error_logger:
        with pytest.raises(Exception, match="Command failed"):
            rpi.get_cpu_info()

        # 驗證 logger.error 被正確調用
        mock_error_logger.assert_called_once_with(
            "Failed to retrieve CPU info: %s", "Command failed"
        )
