# Contents of amd64.system.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
import logging
import math
import re
import traceback
from unit.log_handler import get_logger
from interface.application import BaseInterface

logger = get_logger(__name__, logging.INFO)


class BaseOS(ABC):
    '''docstring'''
    def __init__(self, interface: BaseInterface):
        self.api = interface

    @abstractmethod
    def _get_hyperthreading(self):
        pass

    @abstractmethod
    def _get_memory_size(self):
        pass

    @abstractmethod
    def get_cpu_info(self) -> dict[str, str]:
        pass

    @abstractmethod
    def _get_disk_num(self):
        pass

    @abstractmethod
    def _get_desktop_info(self) -> dict[str]:
        pass

    def _get_pcie_info(self) -> dict[str, str]:
        pass


class AMD64Windows(BaseOS):
    ''' AMD 64 NVMe System
        Any operations of the system that are not included in the DUT behavior

        Attributes:
            interface: Pass object with the 1st argument
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID
            SMART information: critical_warning, temperature, power_cycle,
                unsafe_shutdown
            cpu_num: CPU number
            cpu_name: CPU name
            version: System manufacturer
            serial: Used for indentifying system
    '''
    def __init__(self, interface: BaseInterface):
        self.api = interface
        self.manufacturer = interface.config_file.replace('.json', '')
        self.vid, self.did, self.sdid, self.rev = \
            self._get_pcie_info().values()
        self.cpu_num, self.cpu_name = self.get_cpu_info().values()
        self.vendor, self.model, self.name = self._get_desktop_info().values()
        self.disk_num, self.serial_num = self._get_disk_num().values()
        self.disk_info = self._get_volume()
        self.nic_name = interface.if_name
        self._mac_address = None
        self.memory_size = self._get_memory_size()
        self.hyperthreading = self._get_hyperthreading()
        self.error_features = defaultdict(set)
        self._partition_size = None
        self._disk_capacity = None

    def _get_hyperthreading(self):
        """
        Checks if hyperthreading is enabled on the system.

        Retrieves the number of logical processors and compares it to the
        number of physical cores to determine if hyperthreading is enabled.

        Returns:
            bool: True if hyperthreading is enabled, False otherwise.
        Raises:
            subprocess.CalledProcessError: If there is a problem executing the
                subprocess command
            re.error: If there is an error with regular expression
            ValueError: If the wmic command output can't be processed
        """
        try:
            output = self.api.command_line.original(
                self.api,
                'wmic cpu Get NumberOfCores,NumberOfLogicalProcessors '
                '/Format:List'
            )
            logger.debug('output = %s', output)
            output_string = "".join(output)
            logger.debug('output_string = %s', output_string)
            match = re.search(r'NumberOfLogicalProcessors=(\d+)',
                              output_string)

            if match:
                int_logical_processor = int(match.group(1))
                logger.debug("int_logical_processor = %d",
                             int_logical_processor)
            else:
                raise ValueError("No matching logical processor found.")

            if int_logical_processor/self.cpu_num == 2:
                return True
        except re.error as e:
            logger.error("Invalid regex pattern: %s", e)
            raise
        except Exception as e:
            logger.error('_get_hyperthreading: %s', e)
            raise
        return False

    def _get_memory_size(self):
        """
        Retrieves the total physical memory size in GB.

        Uses the 'wmic' command to query system information and parses the
        output to get the total physical memory size.

        Returns:
            Optional[int]: The total physical memory size in GB, or None if an
            error occurred.

        Raises:
            subprocess.CalledProcessError: If there is a problem executing the
                subprocess command
            ValueError: If the wmic command output can't be converted to int
            AttributeError: If there is no 1-index in the return dictionary
        """
        int_memory_size = None
        try:
            dict_memory_size = self.api.command_line(
                'wmic ComputerSystem get TotalPhysicalMemory')
            logger.debug('dict_memory_size = %s', dict_memory_size)
            if dict_memory_size and len(dict_memory_size) > 1:
                int_memory_size = int(dict_memory_size.get(1))//(1024 ** 3)
                logger.debug('int_memory_size = %d', int_memory_size)
            else:
                raise ValueError("Invalid output format from wmic.")

        except (ValueError, TypeError):  # 在轉換為數字時可能會出錯
            logger.error('Invalid memory value: %s', dict_memory_size)
            raise
        except Exception as e:
            logger.exception('An unexpected error occurred: %s', e)
            raise
        return int_memory_size

    @property
    def mac_address(self):
        ''' Get MAC address
            Parse MAC address from power shell 'Get-NetAdapter'
            Args: None
            Returns: Attribute _mac_address
            Raises: Attribute, Value, and re
        '''
        if hasattr(self, '_mac_address') and self._mac_address:
            return self._mac_address

        try:
            output = self.api.command_line('powershell Get-NetAdapter')
            logger.debug('output = %s', output)

            filtered = output.get(3)
            logger.debug('filtered = %s', filtered)
            if not filtered:
                raise ValueError(
                    "Failed to retrieve the expected output from command.")

            match = re.search(r"([0-9A-Fa-f]{2}(-[0-9A-Fa-f]{2}){5})",
                              filtered)
            if match:
                mac_address = match.group(1)
                logger.debug("Found: %s", mac_address)
                self._mac_address = mac_address
            else:
                raise ValueError("No matching Ethernet adapter found.")
        except AttributeError as e:
            logger.error("AttributeError in mac_address: %s", e)
            raise
        except re.error as e:
            logger.error("Invalid regex pattern in mac_address: %s", e)
            return False
        except Exception as e:
            logger.error("An unexpected error in mac_address: %s", e)
            self._mac_address = None
            raise
        return self._mac_address

    def get_cpu_info(self) -> dict[str, str]:
        ''' Get CPU information
            Grep CPU information from system call 'lscpu'
            Args: None
            Returns: A dictionary consists of CPU(s) and Model Name
            Raises: Logger error
        '''
        str_return = int_cpu_num = str_cpu_name = None
        try:
            str_return = self.api.command_line("wmic cpu get NumberOfCores")
            int_cpu_num = int(str_return.get(1).split(" ")[0])
            str_return = self.api.command_line("wmic cpu get name")
            str_cpu_name = " ".join(str_return.get(1).split(" ")[0:3])
            logger.debug("cpu_num = %d, cpu_name = %s", int_cpu_num,
                         str_cpu_name)
        except ValueError as e:
            logger.error("Value Error in get_cpu_info: %s", e)
            raise
        except Exception as e:
            logger.error('error occurred in get_cpu_info: %s', e)
            raise
        return {"CPU(s)": int_cpu_num, "Model Name": str_cpu_name}

    def _get_disk_num(self):
        """
        Retrieves disk information (number and serial number).

        Uses powershell and findstr to retrieve disk information, with target
        depending on vendor, and parses the output to get the disk number and
        serial number.

        Returns:
            dict[str, str | int | None]: A dictionary containing the disk
            number (as an integer) and serial number (as a string), or None
            for both if an error occurred.

        Raises:
            subprocess.CalledProcessError: If there is a problem executing the
                subprocess command
            ValueError: If the powershell output is not found or can't be
                converted to an integer
            IndexError: If parsing fails
        """
        str_return = int_disk_num = None

        if self.manufacturer == 'VEN_1B4B':
            str_target = 'Marvell'
        else:
            str_target = 'CT500P5SSD8'

        try:
            str_return = self.api.command_line(
                    f'powershell Get-PhysicalDisk|findstr {str_target}')
            logger.debug('str_return = %s', str_return)

            # Check if str_return is None
            if str_return is None:
                raise ValueError("Received None from command_line")

            int_disk_num = int(str_return.get(0).split(' ')[0].lstrip())
            str_serial_num = str_return.get(0).split(' ')[2].lstrip()
            logger.debug('disk_num = %d', int_disk_num)
            logger.debug('serial_num = %s', str_serial_num)

        except Exception as e:
            logger.error('Error occurred in _get_disk_num: %s', e)
            raise
        return {"Number": int_disk_num, "SerialNumber": str_serial_num}

    def _get_desktop_info(self) -> dict[str]:
        ''' Get Desktop Computer information
            Grep HW information from system call 'lshw'
            Args: None
            Returns: A dictionary consists of Version and Serial
            Raises: Logger error
        '''
        str_return = str_model = str_name = None
        try:
            str_return = self.api.command_line(
                'wmic computersystem get Name, Manufacturer, Model')
            if str_return and len(str_return) > 1:
                str_vendor = ' '.join(str_return.get(1).split(' ')[0:1])
                str_model = ' '.join(str_return.get(1).split(' ')[2:4])
                str_name = str_return.get(1).split(' ')[5].lstrip()
            else:
                raise ValueError("Failed to get desktop info.")
            logger.debug('vendor = %s', str_vendor)
            logger.debug('model = %s', str_model)
            logger.debug('name = %s', str_name)

        except Exception as e:
            logger.error('Error occurred in _get_desktop_info: %s', e)
            raise

        return {"Manufacturer": str_vendor,
                "Model": str_model,
                "Name": str_name}

    def _get_pcie_info(self) -> dict[str, str]:
        ''' Get PCIe information
            Grep manufactuer HW IDs from system call ''
            Args: None
            Returns: A dictionary consists of BDF and SDID
            Raises: None
        '''
        dict_return = str_vid = str_did = str_sdid = str_rev = None
        try:
            dict_return = self.api.command_line(
                f"wmic path win32_pnpentity get deviceid,"
                f" name|findstr {self.manufacturer}")
            logger.debug('dict_return type(%s) = %s', type(dict_return),
                         dict_return)

            # Check if str_return is None
            if dict_return is None:
                raise ValueError("Received None from command_line")

            pattern = r"VEN_(\w+)&DEV_(\w+)&SUBSYS_(\w+)&REV_(\w+)"
            match = re.search(pattern, dict_return.get(0))
            if match:
                str_vid, str_did, str_sdid, str_rev = match.groups()
            logger.debug(
                    'manufacturer = %s, vid = %s, did = %s',
                    self.manufacturer, str_vid, str_did)
            logger.debug('sdid = %s, rev = %s', str_sdid, str_rev)

        except Exception as e:
            logger.error('Device not found: %s', e)
            raise
        return {"VID": str_vid, "DID": str_sdid,
                "SDID": str_sdid, "Rev": str_rev}

    def _get_volume(self):
        ''' Get Volume
            Args: None
            Returns: Volume, Size
            Raises: Any errors
        '''
        try:
            # self.disk_num stands for the logical device of target controller
            dict_return = self.api.command_line(
                f"powershell Get-Partition -DiskNumber {self.disk_num}")

            # Get DriveLetter and Size
            pattern = re.compile(r'\d+\s+([A-Z]?)\s+\d+\s+([\d.]+\s+\w+)')

            list_disk_info = []
            logger.debug("dict_return = %s", dict_return)

            if dict_return == {}:
                logger.warning("No partitions found. Attempting to create "
                               "partitions...")
                self.create_partition()

            if isinstance(dict_return, dict):
                output_string = "\n".join(dict_return.values())
            else:
                output_string = dict_return

            for match in pattern.findall(output_string):
                drive_letter = match[0] if match[0] else "No Drive Letter"
                size = match[1]
                list_disk_info.append((drive_letter, size))

            logger.debug("list_disk_info = %s", list_disk_info)

            total_disks = len(list_disk_info)
            logger.debug("Total number of disks: %s", total_disks)

        except Exception as e:
            logger.error('Error occurred in _get_volume: %s', e)
            logger.error("Traceback:\n%s", traceback.format_exc())
            raise

        return list_disk_info

    @property
    def partition_size(self):
        '''Returns the partition size as the next power of 2 based on memory
        size.
        '''
        if self._partition_size is None:
            self._partition_size = self._next_power_of_2(self.memory_size * 2)
        return self._partition_size

    def _next_power_of_2(self, x):
        '''Returns the next power of 2 greater than or equal to x.'''
        return 1 if x == 0 else 2**math.ceil(math.log2(x))

    @property
    def disk_capacity(self):
        ''' Get Volume
        Args: None
        Returns: Volume, Size
        Raises: Any errors
        '''
        try:
            str_return = self.api.command_line(
                "wmic diskdrive get size,caption")

            pattern = r"Marvell_NVMe_Controller\s+(\d+)"

            if str_return:
                if isinstance(str_return, dict):
                    output_string = "\n".join(str_return.values())
                else:
                    output_string = str_return

            match = re.search(pattern, output_string)

            if match:
                disk_capacity = match.group(1)
                logger.debug("disk_capacity = %s", disk_capacity)
            else:
                raise ValueError(
                    "Unexpected None value returned from command line")

        except Exception as e:
            logger.error('Error occurred in disk_capacity: %s', e)
            raise

        return int(disk_capacity) / (2**30)

    def create_partition(self):
        '''Create a partition if none exists
        Args: None
        Returns: None
        Raises: Any errors
        '''
        try:
            diskpart_commands = f"""
            select disk {self.disk_num}
            clean
            convert gpt
            create partition primary
            format fs=ntfs quick
            assign
            """
            # with open('diskpart_script.txt', "w") as file:
            with open(self.api.script_name, "w") as file:
                file.write(diskpart_commands)

            self.api.ftp_command(self.api.script_name)

            partition_cmd = self.api.command_line.original(
                self.api,
                f"diskpart /s {self.api.script_name}"
            )
            result_string = ' '.join(partition_cmd)
            logger.debug('result_string = %s', result_string)

        except OSError as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise Exception("Error during Windows disk partitioning") from e

        except Exception as e:
            logger.error("Error during Windows disk partitioning: %s", e)
            raise


class AMD64Linux(BaseOS):
    '''docstring'''
    def _get_hyperthreading(self):
        pass

    def _get_memory_size(self):
        pass

    def get_cpu_info(self) -> dict[str, str]:
        pass

    def _get_disk_num(self):
        pass

    def _get_desktop_info(self) -> dict[str]:
        pass

    def _get_pcie_info(self) -> dict[str, str]:
        pass


class BasePlatformFactory(ABC):
    """
    Abstract base class for platform factories.

    This class serves as a blueprint for creating platform-specific interfaces
    based on the operating system type. It enforces the implementation of the
    `create_platform` method in subclasses.

    Attributes:
        api (BaseInterface): An interface providing information about the
        platform.
        os_type (str): The operating system type derived from the provided
        `api`.
    """
    def __init__(self, api: BaseInterface):
        """
        Initialize the BasePlatformFactory with an API instance.

        Args:
            api (BaseInterface): An interface instance providing platform
            details.
        """
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def create_platform(self) -> BaseOS:
        """
        Abstract method to create a platform-specific interface.

        Subclasses must implement this method to provide a concrete
        implementation for creating platform-specific objects based on the
        operating system type.

        Returns:
            BaseOS: A platform-specific interface object.
        """
        pass


class PlatformFactory(BasePlatformFactory):
    """
    A concrete implementation of the BasePlatformFactory.

    This class provides a factory method to create platform-specific
    interfaces based on the operating system type. It supports 'Windows' and
    'Linux' platforms.
    """
    def create_platform(self, **kwargs) -> BaseOS:
        """
        Factory method to create a platform-specific interface.

        Depending on the `os_type` attribute, this method creates an instance
        of a platform-specific class (e.g., `AMD64Windows` or `AMD64Linux`).

        Args:
            **kwargs: Additional arguments passed to the platform-specific
            class constructor.

        Returns:
            BaseOS: An instance of the platform-specific class.

        Raises:
            ValueError: If the `os_type` is not supported.
        """
        if self.os_type == 'Windows':
            return AMD64Windows(**kwargs)
        elif self.os_type == 'Linux':
            return AMD64Linux(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
