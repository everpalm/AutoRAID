# Content of conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
# from amd_desktop.amd64_event import WindowsEvent
# from unittest.mock import MagicMock
import logging
import pytest

# logging.getLogger("pymongo").setLevel(logging.CRITICAL)
# logging.getLogger('amd_desktop.amd64_event').setLevel(logging.INFO)
# logging.getLogger('unit.application_interface').setLevel(logging.CRITICAL)
# logging.getLogger('unit.ping').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


# @pytest.fixture(scope="session")
# def gitlab_api(request):
#     return request.config._store.get('gitlab_api', None)


# 創建 platform_mock 的 fixture
# @pytest.fixture(scope="module")
# def platform_mock():
#     return MagicMock()


# 創建 WindowsEvent 實例的 fixture，並注入 platform_mock
# @pytest.fixture(scope="function")
# def windows_event(platform_mock):
#     windows_event = WindowsEvent(platform_mock, 'config_file.json')
#     windows_event._api = MagicMock()  # 預設 Mock _api
#     return windows_event




    


    