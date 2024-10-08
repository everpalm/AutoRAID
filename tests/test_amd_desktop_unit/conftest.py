# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
from amd_desktop.amd64_event import WindowsEvent
from unittest.mock import MagicMock
import logging
import pytest

logging.getLogger('amd_desktop.amd64_event').setLevel(logging.INFO)

logger = logging.getLogger(__name__)


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




    


    