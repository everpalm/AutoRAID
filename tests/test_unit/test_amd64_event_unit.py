import pytest
from unittest.mock import MagicMock, patch
from collections import defaultdict
import re
from amd_desktop.amd64_nvme import AMD64NVMe
from amd_desktop.amd64_event import WindowsEvent  # 引入 WindowsEvent 類，確保正確的模組名稱

# 測試 WindowsEvent 的 find_error 方法
@pytest.fixture
def mock_platform():
    mock_platform = MagicMock(spec=AMD64NVMe)
    # 模擬 api 和 command_line
    mock_platform.api = MagicMock()  # 添加 api 屬性
    mock_platform.api.command_line = MagicMock()  # 添加 command_line 子屬性
    mock_platform.api.command_line._original = MagicMock()  # 添加 _original 方法
    
    mock_platform.error_features = defaultdict(set)
    return mock_platform

def test_find_error_success(mock_platform):
    # 假設 PowerShell 的輸出
    mock_platform.api.command_line._original.return_value = [
        'Event 157: Disk 1 has been surprise removed.'
    ]

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)
    
    # 定義日誌事件查找條件
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'
    
    # 調用 find_error 方法
    result = win_event.find_error(log_name, event_id, pattern)
    
    # 驗證結果
    assert result is True
    assert event_id in mock_platform.error_features
    assert '1' in mock_platform.error_features[event_id]

def test_find_error_no_match(mock_platform):
    # 模擬沒有匹配的輸出
    mock_platform.api.command_line._original.return_value = [
        'Event 158: Another event.'
    ]

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 find_error 方法
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    result = win_event.find_error(log_name, event_id, pattern)

    # 沒有匹配應該返回 False
    assert result is False
    assert event_id not in mock_platform.error_features

def test_find_error_empty_output(mock_platform):
    # 模擬 PowerShell 沒有返回任何輸出
    mock_platform.api.command_line._original.return_value = []

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 find_error 方法
    log_name = "System"
    event_id = 157
    pattern = r'Disk (\d+) has been surprise removed.'

    result = win_event.find_error(log_name, event_id, pattern)

    # 沒有輸出應該返回 False
    assert result is False

def test_clear_error_success(mock_platform):
    # 模擬 PowerShell 清除日誌成功
    mock_platform.api.command_line._original.return_value = "Log cleared."

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法
    result = win_event.clear_error()

    # 應該返回 True
    assert result is True
    mock_platform.api.command_line._original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )

def test_clear_error_failure(mock_platform):
    # 模擬 PowerShell 清除日誌失敗
    mock_platform.api.command_line._original.side_effect = Exception("Command failed")

    # 初始化 WindowsEvent
    win_event = WindowsEvent(mock_platform)

    # 調用 clear_error 方法
    result = win_event.clear_error()

    # 應該返回 False，且記錄錯誤
    assert result is False
    mock_platform.api.command_line._original.assert_called_once_with(
        mock_platform.api, 'powershell "Clear-EventLog -LogName system"'
    )
