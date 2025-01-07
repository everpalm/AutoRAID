'''Unit tests for WindowsEvent class methods related to log management.
   This module verifies the behavior of methods within the WindowsEvent
   class, including the ability to find error logs based on patterns and
   clear system event logs, using mocked platform interactions to simulate
   command-line responses.

   Copyright (c) 2024 Jaron Cheng
'''
from unittest.mock import MagicMock
from collections import defaultdict
import pytest
from amd64.amd64_nvme import AMD64NVMe
from amd64.amd64_event import WindowsEvent


# 定義一個 fixture 來設置 mock_platform 及其 api 屬性
@pytest.fixture
def mock_platform():
    """Fixture that sets up a mocked platform, including mock attributes for
    the AMD64NVMe class with simulated `api` and `command_line` attributes.

    Returns:
        MagicMock: A mock object simulating AMD64NVMe platform behavior with
                   error_features and command-line interaction.
    """
    # 模擬 AMD64NVMe 的 platform 和 api 行為
    mocked = MagicMock(spec=AMD64NVMe)

    # 模擬 error_features
    mocked.error_features = defaultdict(set)

    # 手動設置 mock 的 api 和 command_line
    mocked.api = MagicMock()  # 添加 api 屬性
    mocked.api.command_line = MagicMock()  # 添加 command_line 屬性
    mocked.api.command_line.original = MagicMock()  # 添加 original 方法

    return mocked


# 測試 find_error 方法匹配成功的情況
def test_find_error_match_found(mock_platform):
    """Tests the `find_error` method of the WindowsEvent class for a case
    where a matching pattern is found in the command output.

    Args:
        mock_platform (MagicMock): Mocked platform fixture with simulated
                                   command-line response.

    Verifies:
        - `find_error` returns True when pattern matches.
        - Matching event details are added to error_features.
    """
    # 模擬 original 方法的返回值
    mock_platform.api.command_line.original.return_value = [
        'Disk 1 has been surprise removed.'
    ]

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 測試數據
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    # 調用 find_error，應該返回 True
    result = win_event.find_error(log_name, event_id, pattern)

    # 驗證返回 True 並且正確添加匹配的值
    assert result is True
    assert '1' in mock_platform.error_features[event_id]


# 測試 find_error 方法沒有匹配的情況
def test_find_error_no_match(mock_platform):
    """Tests the `find_error` method for a case where no matching pattern
    is found in the command output.

    Args:
        mock_platform (MagicMock): Mocked platform with no matching pattern.

    Verifies:
        - `find_error` returns False when there is no match.
        - error_features dictionary remains unchanged.
    """
    # 模擬沒有匹配的輸出
    mock_platform.api.command_line.original.return_value = [
        'Event 158: Another event.'
    ]

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 測試數據
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    # 調用 find_error，應該返回 False
    result = win_event.find_error(log_name, event_id, pattern)
    assert result is False
    assert event_id in mock_platform.error_features


# 測試 find_error 方法在輸出為空的情況下
def test_find_error_empty_output(mock_platform):
    """Tests the `find_error` method with an empty command output.

    Args:
        mock_platform (MagicMock): Mocked platform with empty command output.

    Verifies:
        - `find_error` returns False when the output is empty.
    """
    # 模擬 PowerShell 沒有返回任何輸出
    mock_platform.api.command_line.original.return_value = []

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 測試數據
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    # 調用 find_error，應該返回 False
    result = win_event.find_error(log_name, event_id, pattern)
    assert result is False


# 測試 clear_error 方法
def test_clear_error_success(mock_platform):
    """Tests the `clear_error` method for successful log clearing.

    Args:
        mock_platform (MagicMock): Mocked platform where `clear_error`
        simulates a successful log clearing operation.

    Verifies:
        - `clear_error` returns True when log clearing is successful.
        - Correct command is sent to the command line once.
    """
    # 模擬 PowerShell 成功清除日誌
    mock_platform.api.command_line.original.return_value = "Log cleared."

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法
    result = win_event.clear_error()
    assert result is True
    mock_platform.api.command_line.original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )


# 測試 clear_error 方法的異常情況
def test_clear_error_failure(mock_platform):
    """Tests the `clear_error` method for a failure scenario where an exception
    is raised during log clearing.

    Args:
        mock_platform (MagicMock): Mocked platform with `clear_error` command
                                   triggering an exception.

    Verifies:
        - `clear_error` returns False when an exception is raised.
        - Correct command is sent to the command line once.
    """
    # 模擬 PowerShell 命令執行失敗
    mock_platform.api.command_line.original.side_effect = Exception(
        "Command failed")

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法，應該返回 False
    result = win_event.clear_error()
    assert result is False
    mock_platform.api.command_line.original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )
