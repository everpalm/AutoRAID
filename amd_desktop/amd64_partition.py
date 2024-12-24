# Contents of amd64_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from abc import ABC
from abc import abstractmethod
from amd_desktop.amd64_nvme import AMD64NVMe
from typing import List
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class ParitionDisk(ABC):
    """Abstract base class for disk partitioning operations."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the warm boot process."""


class WindowsVolume(ParitionDisk):
    """Disk partitioning implementation for Windows systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def startup(self) -> bool:
        logger.info("Startup diskpart...")
        try:
            # Execute the warm boot command
            self._api.command_line.original(self._api, 'diskpart')
            logger.info("Start diskpart...")
            return True

        except Exception as e:
            logger.error("Error startup diskpart: %s", e)
            return False

    def close(self) -> bool:
        logger.info("Exit diskpart...")
        try:
            self._api.command_line.original(self._api, 'exit')
            logger.info("Close diskpart...")
            return True

        except Exception as e:
            logger.error("Error close diskpart: %s", e)
            return False

    def execute(self) -> List:
        logger.info("Disk partitioning for Windows...")
        try:
            # Execute the warm boot command
            parition_cmd = self._api.command_line.original(self._api,
                                                           'dir')
            logger.info("Disk partitioning successfully for Windows.")
            return parition_cmd

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            return -1


class LinuxVolume(ParitionDisk):
    """Disk partitioning implementation for Linux systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Disk paritioining for Linux...")
        try:
            # Execute the warm boot command
            self._api.command_line(self._api, 'ls')
            logger.info("Disk paritioning successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux partitioning: %s", e)
            return False
