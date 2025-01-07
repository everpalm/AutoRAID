# Contents of amd64_warmboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging

from abc import ABC, abstractmethod
from amd64.amd64_nvme import AMD64NVMe
from interface.application import BaseInterface
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class WarmBoot(ABC):
    """Abstract base class for warm boot operations."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the warm boot process."""


class WindowsWarmBoot(WarmBoot):
    """Warm boot implementation for Windows systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Executing warm boot for Windows...")
        try:
            # Execute the warm boot command
            self._api.command_line.original(self._api, 'shutdown /r /t 0')
            logger.info("Warm boot executed successfully for Windows.")
            return True

        except Exception as e:
            logger.error("Error during Windows warm boot execution: %s", e)
            return False


class LinuxWarmBoot(WarmBoot):
    """Warm boot implementation for Linux systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Executing warm boot for Linux...")
        try:
            # Execute the warm boot command
            self._api.command_line(self._api, 'sudo reboot')
            logger.info("Warm boot executed successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux warm boot execution: %s", e)
            return False


class BaseWarmBootFactory(ABC):
    '''docstring'''
    def __init__(self, api: BaseInterface):
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def initiate(self, os_type: str, **kwargs) -> WarmBoot:
        pass


class WarmBootFactory(BaseWarmBootFactory):
    # def initiate(self, os_type: str, **kwargs) -> WarmBoot:
    def initiate(self, **kwargs) -> WarmBoot:
        if self.os_type == 'Windows':
            return WindowsWarmBoot(**kwargs)
        elif self.os_type == 'Linux':
            return LinuxWarmBoot(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
