from amd_desktop.amd64_event import WindowsEvent
from collections import defaultdict
from unittest.mock import MagicMock
import pytest

# 創建 platform_mock 的 fixture
@pytest.fixture(scope="module")
def platform_mock():
    return MagicMock()


# 創建 WindowsEvent 實例的 fixture，並注入 platform_mock
@pytest.fixture(scope="function")
def windows_event(platform_mock):
    windows_event = WindowsEvent(platform_mock, 'config_file.json')
    windows_event._api = MagicMock()  # 預設 Mock _api
    return windows_event


# 測試類別
class TestAMD64Event:

    def test_find_error_success(self, windows_event):
        # 模擬成功的 API 調用
        windows_event._api.command_line._original.return_value = [
            "EventID: 1234, ErrorCode: 500, Message: Sample error message",
            "EventID: 1234, ErrorCode: 400, Message: Another error message"
        ]

        # 測試 find_error 方法
        result = windows_event.find_error("Application", 1234, r"ErrorCode: (\d+)")
        
        # 確認 find_error 返回 True
        assert result == True

        # 檢查 error_features 是否正確填充
        expected_error_features = {1234: ['500', '400']}
        assert windows_event.error_features == expected_error_features

        # 驗證命令是否正確執行
        windows_event._api.command_line._original.assert_called_once_with(
            windows_event._api,
            'powershell "Get-EventLog -LogName Application|Where-Object { $_.EventID -eq 1234 }"'
        )

    def test_find_error_no_match(self, windows_event):
        # 模擬無匹配的 API 調用
        windows_event._api.command_line._original.return_value = []

        # 測試 find_error 方法
        result = windows_event.find_error("Application", 1234, r"ErrorCode: (\d+)")
        
        # 確認 find_error 返回 False
        assert result == False

        # 檢查 error_features 應保持空
        assert windows_event.error_features == defaultdict(list)

        # 驗證命令是否正確執行
        windows_event._api.command_line._original.assert_called_once_with(
            windows_event._api,
            'powershell "Get-EventLog -LogName Application|Where-Object { $_.EventID -eq 1234 }"'
        )

    def test_find_error_exception(self, windows_event):
        # 模擬 API 調用拋出異常
        windows_event._api.command_line._original.side_effect = Exception("Command failed")

        # 測試 find_error 方法
        result = windows_event.find_error("Application", 1234, r"ErrorCode: (\d+)")
        
        # 確認 find_error 返回 False
        assert result == False

        # 檢查 error_features 應保持空
        assert windows_event.error_features == defaultdict(list)

    def test_config_file_property(self, windows_event):
        # 測試 config_file 的 getter
        # assert windows_event.config_file == 'config/config_file.json'
        assert windows_event.config_file == 'config_file.json'

        # 測試 config_file 的 setter
        windows_event.config_file = 'new_config.json'
        # assert windows_event.config_file == 'config/new_config.json'
        assert windows_event.config_file == 'new_config.json'
