import pytest
from amd_desktop.amd64_warmboot import WindowsWarmBoot
from amd_desktop.amd64_warmboot import LinuxWarmBoot

@pytest.fixture
def mock_api(mocker):
    """Fixture to create a mocked API."""
    api = mocker.Mock()
    api.command_line = mocker.Mock()
    api.command_line._original = mocker.Mock()
    return api

# WindowsWarmBoot Tests
def test_windows_execute_success(mock_api, mocker):
    """Test successful execution of Windows warm boot."""
    platform = mocker.Mock(api=mock_api)
    windows_warmboot = WindowsWarmBoot(platform)

    # 模擬成功執行
    mock_api.command_line._original.return_value = None  # 模擬正常返回

    assert windows_warmboot.execute() is True
    mock_api.command_line._original.assert_called_once_with(mock_api,
                                                            'shutdown /r /t 0')

def test_windows_execute_failure(mock_api, mocker):
    """Test failure during Windows warm boot execution."""
    platform = mocker.Mock(api=mock_api)
    windows_warmboot = WindowsWarmBoot(platform)

    # 模擬執行失敗
    mock_api.command_line._original.side_effect = Exception(
        "Mocked exception")

    assert windows_warmboot.execute() is False
    mock_api.command_line._original.assert_called_once_with(mock_api,
                                                            'shutdown /r /t 0')

# LinuxWarmBoot Tests
def test_linux_execute_success(mock_api, mocker):
    """Test successful execution of Linux warm boot."""
    platform = mocker.Mock(api=mock_api)
    linux_warmboot = LinuxWarmBoot(platform)

    # 模擬成功執行
    mock_api.command_line.return_value = None  # 模擬正常返回

    assert linux_warmboot.execute() is True
    mock_api.command_line.assert_called_once_with(mock_api, 'sudo reboot')


def test_linux_execute_failure(mock_api, mocker):
    """Test failure during Linux warm boot execution."""
    platform = mocker.Mock(api=mock_api)
    linux_warmboot = LinuxWarmBoot(platform)

    # 模擬執行失敗
    mock_api.command_line.side_effect = Exception("Mocked exception")

    assert linux_warmboot.execute() is False
    mock_api.command_line.assert_called_once_with(mock_api, 'sudo reboot')
