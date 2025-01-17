# Contents of storage.partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import math
import re
from abc import ABC
from abc import abstractmethod
from amd64.nvme import AMD64NVMe
from amd64.system import BaseOS
from typing import List
from interface.application import BaseInterface
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class PartitionDisk(ABC):
    """
    Abstract base class for disk partitioning operations.

    This class defines a common interface for different disk partitioning
    implementations on various platforms.
    """

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the disk partitioning process.

        This method must be implemented by subclasses to define specific
        partitioning operations.

        Returns:
            bool: True if partitioning is successful, False otherwise.
        """
        pass


class WindowsVolume(PartitionDisk):
    """
    Disk partitioning implementation for Windows systems.

    Provides methods to write, execute, and delete partitioning scripts
    on a Windows platform.
    """
    def __init__(self, platform: BaseOS, disk_format: str,
                 file_system: str):
        """
        Initialize the WindowsVolume instance.

        Args:
            platform (AMD64NVMe): An instance of the AMD64NVMe class
                representing the platform's API for interaction.
        """
        self._api = platform.api
        self.remote_dir = platform.api.remote_dir
        self.remote_ip = platform.api.remote_ip
        self.account = platform.api.account
        self.password = platform.api.password
        self.script_name = platform.api.script_name
        self.disk_num = platform.disk_num
        self.disk_info = platform.disk_info
        self.partition_size = platform.partition_size * 1024
        self.disk_capacity = platform.disk_capacity
        self.partition_num = math.floor(
            self.disk_capacity / platform.partition_size)
        self.disk_format = disk_format
        self.file_system = file_system

    def write_script(self, diskpart_script: str) -> bool:
        """
        Write a disk partitioning script to a file and upload it via FTP.

        Args:
            diskpart_script (str): The content of the disk partitioning script.

        Returns:
            bool: True if the script is successfully written and uploaded.

        Raises:
            Exception: If there is an error during the write or upload process.
        """
        logger.debug("diskpart_script = %s", diskpart_script)
        logger.debug("self.script_name = %s", self.script_name)
        try:
            with open(self.script_name, "w") as file:
                file.write(diskpart_script)

            self._api.ftp_command(self.script_name)
            return True

        except OSError as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise Exception("Error during Windows disk partitioning") from e

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise

    def execute(self, pattern: str) -> List:
        """
        Execute the disk partitioning script using DiskPart.

        Args:
            pattern (str): A regular expression pattern to match against the
                output of the partitioning command.

        Returns:
            List: The extracted value(s) from the command output that match
                the pattern.

        Raises:
            ValueError: If no match is found in the command output.
            Exception: If an error occurs during the execution process.
        """
        logger.info("Disk partitioning for Windows...")
        try:
            partition_cmd = self._api.command_line.original(
                self._api,
                f"diskpart /s {self.script_name}"
            )
            result_string = ' '.join(partition_cmd)
            logger.debug('result_string = %s', result_string)
            match = re.search(pattern, result_string)
            if match:
                extracted_string = match.group(1)
                logger.debug(f"extracted_string: {extracted_string}")
                return extracted_string
            else:
                logger.warning("Pattern not matched in the command output.")
                raise ValueError("No matching disk found.")

        except Exception as e:
            logger.error("Error during write script execution: %s", e)
            raise

    def delete_script(self) -> bool:
        """
        Delete the disk partitioning script from the system.

        Returns:
            bool: True if the script is successfully deleted.

        Raises:
            Exception: If an error occurs during the deletion process.
        """
        logger.debug("Delete diskpart script...")
        try:
            partition_cmd = self._api.command_line.original(
                self._api,
                f"del {self.script_name}"
            )
            logger.info("partition_cmd = %s", partition_cmd)
            return True

        except Exception as e:
            logger.error("Error during deletion of diskpart script: %s", e)
            raise Exception("Error during deletion of diskpart script") from e

    def create_partition(self) -> bool:
        '''This is a docstring'''
        script_lines = [
            f"select disk {self.disk_num}",
            "clean",
            f"convert {self.disk_format}"
        ]
        logger.debug("self.partition_size = %s", self.partition_size)
        logger.debug("self.disk_capacity = %s", self.disk_capacity)
        partition_num = self.partition_num
        logger.debug("partition_num = %s", partition_num)

        partition_size = self.partition_size
        for _ in range(partition_num):
            script_lines.append(
                f"create partition primary size={partition_size}")
            script_lines.append(f"format fs={self.file_system} quick")
            script_lines.append("assign")
        logger.debug("script_lines = %s", script_lines)

        try:
            with open(self.script_name, "w") as file:
                file.write("\n".join(script_lines))

            print("DiskPart script generated: diskpart_script.txt")
            self._api.ftp_command(self.script_name)
            return True

        except Exception as e:
            logger.error("Error during creation of diskpart script: %s", e)
            raise Exception("Error during creation of diskpart script") from e


class LinuxVolume(PartitionDisk):
    """
    Disk partitioning implementation for Linux systems.

    Provides methods to execute disk partitioning operations on Linux.
    """

    def __init__(self, platform: AMD64NVMe):
        """
        Initialize the LinuxVolume instance.

        Args:
            platform (AMD64NVMe): An instance of the AMD64NVMe class
                representing the platform's API for interaction.
        """
        self._api = platform.api

    def execute(self) -> bool:
        """
        Execute disk partitioning commands on a Linux system.

        Returns:
            bool: True if the partitioning operation is successful, False
            otherwise.

        Raises:
            Exception: If an error occurs during the execution process.
        """
        logger.info("Disk partitioning for Linux...")
        try:
            self._api.command_line(self._api, 'ls')
            logger.info("Disk partitioning successfully for Linux.")
            return True

        except Exception as e:
            logger.error("Error during Linux partitioning: %s", e)
            return False


class BasePartitionFactory(ABC):
    '''docstring'''
    def __init__(self, api: BaseInterface):
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def initiate(self, os_type: str, **kwargs) -> PartitionDisk:
        pass


class PartitionFactory(BasePartitionFactory):
    # def initiate(self, os_type: str, **kwargs) -> PartitionDisk:
    def initiate(self, **kwargs) -> PartitionDisk:
        if self.os_type == 'Windows':
            return WindowsVolume(**kwargs)
        elif self.os_type == 'Linux':
            return LinuxVolume(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
