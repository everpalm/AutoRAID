# Contents of amd64_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
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

    def write_script(self, diskpart_script: str) -> bool:
        logger.debug("diskpart_script = %s", diskpart_script)
        logger.debug("self.script_name = %s", self.script_name)
        try:
            with open(self.script_name, "w") as file:
                file.write(diskpart_script)

            self._api.ftp_command(self.script_name)

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise

    def execute(self, pattern: str) -> List:
        logger.info("Disk partitioning for Windows...")
        try:
            parition_cmd = self._api.command_line.original(
                self._api,
                f"diskpart /s {self.script_name}"
            )
            logger.info("Disk partitioning successfully for Windows.")
            result_string = ' '.join(parition_cmd)
            match = re.search(pattern, result_string)
            if match:
                extracted_string = match.group(1)
                print(f"extracted_string: {extracted_string}")
                return extracted_string
            else:
                raise ValueError("No matching disk found.")

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise

    def delete_script(self) -> bool:
        logger.info("Delete diskpart script...")
        try:
            parition_cmd = self._api.command_line.original(
                self._api,
                f"del {self.script_name}"
            )
            logger.info("Delete diskpart script successfully")
            return parition_cmd

        except Exception as e:
            logger.error("Error during deletion of diskpart script: %s", e)
            raise


class LinuxVolume(ParitionDisk):
    """Disk partitioning implementation for Linux systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Disk paritioining for Linux...")
        try:
            self._api.command_line(self._api, 'ls')
            logger.info("Disk paritioning successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux partitioning: %s", e)
            return False
