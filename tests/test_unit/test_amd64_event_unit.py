import pytest
from unittest.mock import MagicMock
from collections import defaultdict
from amd_desktop.amd64_nvme import AMD64NVMe
from amd_desktop.amd64_event import WindowsEvent, MatchFoundException  # 修改為你的模組名稱

# 定義一個 fixture 來設置 mock_platform 及其 api 屬性
@pytest.fixture
def mock_platform():
    # 模擬 AMD64NVMe 的 platform 和 api 行為
    mock_platform = MagicMock(spec=AMD64NVMe)
    
    # 手動設置 mock 的 api 和 command_line
    mock_platform.api = MagicMock()  # 添加 api 屬性
    mock_platform.api.command_line = MagicMock()  # 添加 command_line 屬性
    mock_platform.api.command_line._original = MagicMock()  # 添加 _original 方法

    # 模擬 error_features
    mock_platform.error_features = defaultdict(set)
    
    return mock_platform

# 測試 find_error 方法匹配成功的情況，應引發 MatchFoundException
def test_find_error_match_found(mock_platform):
    # 模擬 _original 方法的返回值
    mock_platform.api.command_line._original.return_value = [
        'Disk 1 has been surprise removed.'
    ]
    
    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 測試數據
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    # 測試是否引發 MatchFoundException
    with pytest.raises(MatchFoundException) as excinfo:
        win_event.find_error(log_name, event_id, pattern)

    # 驗證 MatchFoundException 被正確引發
    assert str(excinfo.value) == "Match found for event ID 157: 1"
    assert '1' in mock_platform.error_features[event_id]

# 測試 find_error 方法沒有匹配的情況
def test_find_error_no_match(mock_platform):
    # 模擬沒有匹配的輸出
    mock_platform.api.command_line._original.return_value = [
        'Event 158: Another event.'
    ]

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 測試數據
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    # 調用 find_error，應該不會引發異常並返回 False
    result = win_event.find_error(log_name, event_id, pattern)
    assert result is False
    assert event_id not in mock_platform.error_features

# 測試 find_error 方法在輸出為空的情況下
def test_find_error_empty_output(mock_platform):
    # 模擬 PowerShell 沒有返回任何輸出
    mock_platform.api.command_line._original.return_value = []

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
    # 模擬 PowerShell 成功清除日誌
    mock_platform.api.command_line._original.return_value = "Log cleared."

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法
    result = win_event.clear_error()
    assert result is True
    mock_platform.api.command_line._original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )

# 測試 clear_error 方法的異常情況
def test_clear_error_failure(mock_platform):
    # 模擬 PowerShell 命令執行失敗
    mock_platform.api.command_line._original.side_effect = Exception("Command failed")

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法，應該返回 False
    result = win_event.clear_error()
    assert result is False
    mock_platform.api.command_line._original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )
