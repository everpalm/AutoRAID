import pytest
from unittest.mock import patch, MagicMock
from arm.system import RaspberryPi, CPUInformation, SystemInformation
from interface.application import BaseInterface


@pytest.fixture
def mock_api():
    mock = MagicMock(spec=BaseInterface)
    mock.config_file = "test_config.json"
    return mock


@pytest.fixture
def raspberry_pi(mock_api):
    return RaspberryPi(uart_path="/dev/ttyAMA0", baud_rate=115200, file_name="logfile.log", rpi_api=mock_api)


def test_open_uart(raspberry_pi, mock_api):
    raspberry_pi.open_uart()

    # 確認執行了 pwd 和 screen 命令
    mock_api.command_line.assert_any_call('pwd')
    mock_api.command_line.assert_any_call(
        'sudo screen -dm -L -Logfile logfile.log /dev/ttyAMA0 115200'
    )


def test_close_uart(raspberry_pi, mock_api):
    # 模擬 screen -ls 輸出
    mock_api.command_line.return_value = {1: '1234..some-session-info'}

    result = raspberry_pi.close_uart()

    # 確認解析的 UART port 是否正確
    assert result == 1234

    # 確認關閉命令是否被執行
    mock_api.command_line.assert_any_call('sudo screen -ls')
    mock_api.command_line.assert_any_call('sudo screen -X -S 1234 quit')


def test_get_memory_size(raspberry_pi, mock_api):
    mock_api.command_line.original.return_value = ['MemTotal:       2048000 kB']

    memory_size = raspberry_pi._get_memory_size()

    assert memory_size == (2048000, 'kB')


def test_get_cpu_info(raspberry_pi, mock_api):
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
