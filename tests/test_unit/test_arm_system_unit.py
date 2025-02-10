import pytest
from unittest.mock import MagicMock
from system.arm import RaspberryPi, CPUInformation, SystemInformation
from interface.application import BaseInterface


@pytest.fixture
def mock_api():
    """Mock BaseInterface with required attributes and methods."""
    mock = MagicMock(spec=BaseInterface)
    mock.config_file = "test_config.json"
    mock.manufacturer = "MockManufacturer"
    mock.model = "MockModel"
    mock.command_line.return_value = "MockCommand"
    return mock


@pytest.fixture
def raspberry_pi(mock_api):
    """Fixture to create a RaspberryPi instance."""
    return RaspberryPi(uart_path="/dev/ttyAMA0", baud_rate=115200,
                       file_name="logfile.log", rpi_api=mock_api)


def test_open_uart(raspberry_pi, mock_api):
    """Test the open_uart method."""
    raspberry_pi.open_uart()

    # 確認執行了 pwd 和 screen 命令
    mock_api.command_line.assert_any_call('pwd')
    mock_api.command_line.assert_any_call(
        'sudo screen -dm -L -Logfile logfile.log /dev/ttyAMA0 115200'
    )


def test_close_uart_success(raspberry_pi, mock_api):
    """Test the close_uart method when a valid UART port is found."""
    mock_api.command_line.return_value = {1: '1234..some-session-info'}

    result = raspberry_pi.close_uart()

    # 確認解析的 UART port 是否正確
    assert result == 1234

    # 確認關閉命令是否被執行
    mock_api.command_line.assert_any_call('sudo screen -ls')
    mock_api.command_line.assert_any_call('sudo screen -X -S 1234 quit')


def test_close_uart_no_sessions(raspberry_pi, mock_api):
    """Test the close_uart method when no UART sessions are found."""
    mock_api.command_line.return_value = {}

    result = raspberry_pi.close_uart()

    # 應返回 -1，表示沒有找到 session
    assert result == -1


def test_close_uart_invalid_port(raspberry_pi, mock_api):
    """Test the close_uart method when an invalid UART port is found."""
    mock_api.command_line.return_value = {1: 'invalid..session'}

    result = raspberry_pi.close_uart()

    # 應返回 -1，表示無法解析有效的 UART port
    assert result == -1


def test_get_memory_size(raspberry_pi, mock_api):
    """Test the _get_memory_size method."""
    mock_api.command_line.original.return_value = \
        ['MemTotal:       2048000 kB']

    memory_size = raspberry_pi._get_memory_size()

    assert memory_size == (2048000, 'kB')


def test_get_cpu_info(raspberry_pi, mock_api):
    """Test the get_cpu_info method."""
    mock_api.command_line.original.side_effect = [
        ["Vendor ID:ARM"],
        ["Model name:Cortex-A72"]
    ]

    cpu_info = raspberry_pi.get_cpu_info()

    assert cpu_info == CPUInformation(
        vendor_name="ARM",
        model_name="Cortex-A72",
        hyperthreading=False
    )


def test_get_system_info(raspberry_pi, mock_api):
    """Test the get_system_info method."""
    mock_api.command_line.original.side_effect = [
        ["Model           : Raspberry Pi 4 Model B Rev 1.2"],
        ["MY-RASPI-02"]
    ]

    system_info = raspberry_pi.get_system_info()

    assert system_info == SystemInformation(
        manufacturer="Raspberry Pi 4",
        model="B",
        name="MY-RASPI-02",
        rev="1.2"
    )
