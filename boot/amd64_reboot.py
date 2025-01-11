# Contents of amd64_warmboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from abc import ABC
from abc import abstractmethod
from amd64.nvme import AMD64NVMe
from interface.application import BaseInterface
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class BaseReboot(ABC):
    """Abstract base class for warm boot operations."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    @abstractmethod
    def warm_reset(self) -> bool:
        """Execute the warm boot process."""

    @abstractmethod
    def cold_reset(self) -> bool:
        """Execute the cold boot process."""


class WindowsReboot(BaseReboot):
    """Warm boot implementation for Windows systems."""

    def warm_reset(self) -> bool:
        logger.info("Executing warm boot for Windows...")
        try:
            # Execute the warm boot command
            self._api.command_line.original(self._api, 'shutdown /r /t 0')
            logger.info("Warm boot executed successfully for Windows.")
            return True

        except Exception as e:
            logger.error("Error during Windows warm boot execution: %s", e)
            return False

    def cold_reset(self) -> bool:
        logger.info("Executing warm boot for Windows...")
        try:
            # Execute the warm boot command
            self._api.command_line.original(self._api, 'shutdown /s /t 0')
            logger.info("Cold boot executed successfully for Windows.")
            return True

        except Exception as e:
            logger.error("Error during Windows cold boot execution: %s", e)
            return False


class LinuxReboot(BaseReboot):
    """Warm boot implementation for Linux systems."""

    def warm_reset(self) -> bool:
        logger.info("Executing warm boot for Linux...")
        try:
            # Execute the warm boot command
            self._api.command_line(self._api, 'sudo shutdown -r now')
            logger.info("Warm boot executed successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux warm boot execution: %s", e)
            return False

    def cold_reset(self) -> bool:
        logger.info("Executing warm boot for Linux...")
        try:
            # Execute the warm boot command
            self._api.command_line(self._api, 'sudo shutdown -h now')
            logger.info("Cold boot executed successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux cold boot execution: %s", e)
            return False


class BaseRebootFactory(ABC):
    '''docstring'''
    def __init__(self, api: BaseInterface):
        '''docstring'''
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def initiate(self, os_type: str, **kwargs) -> BaseReboot:
        '''docstring'''
        pass


class RebootFactory(BaseRebootFactory):
    '''docstring'''
    def initiate(self, **kwargs) -> BaseReboot:
        '''docstring'''
        if self.os_type == 'Windows':
            return WindowsReboot(**kwargs)
        elif self.os_type == 'Linux':
            return LinuxReboot(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
