# Contents of amd64_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from abc import ABC
from abc import abstractmethod
from amd_desktop.amd64_nvme import AMD64NVMe
from typing import List
from unit.log_handler import get_logger
# import paramiko

logger = get_logger(__name__, logging.DEBUG)


class ParitionDisk(ABC):
    """Abstract base class for disk partitioning operations."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the warm boot process."""


class WindowsVolume(ParitionDisk):
    """Disk partitioning implementation for Windows systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api
        self.remote_dir = platform.api.remote_dir
        self.remote_ip = platform.api.remote_ip
        self.account = platform.api.account
        self.password = platform.api.password
        self.script_name = platform.api.script_name
    # def startup(self) -> bool:
    #     logger.info("Startup diskpart...")
    #     try:
    #         # Execute the warm boot command
    #         self._api.command_line.original(self._api, 'diskpart')
    #         logger.info("Start diskpart...")
    #         return True

    #     except Exception as e:
    #         logger.error("Error startup diskpart: %s", e)
    #         return False

    # def close(self) -> bool:
    #     logger.info("Exit diskpart...")
    #     try:
    #         self._api.command_line.original(self._api, 'exit')
    #         logger.info("Close diskpart...")
    #         return True

    #     except Exception as e:
    #         logger.error("Error close diskpart: %s", e)
    #         return False
    def write_script(self, diskpart_script) -> bool:
        logger.debug("diskpart_script = %s", diskpart_script)
        try:
            with open("diskpart_script.txt", "w") as file:
                file.write(diskpart_script)

            logger.debug("self.script_name = ", self.script_name)
            self._api.ftp_command(self.script_name)

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            return -1

    def execute(self) -> List:
        logger.info("Disk partitioning for Windows...")
        try:
            # Execute the warm boot command
            parition_cmd = self._api.command_line.original(
                self._api,
                r"diskpart /s diskpart_script.txt"
            )
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
