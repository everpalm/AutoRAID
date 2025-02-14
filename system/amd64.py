# Contents of system/amd64.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
# from dataclasses import dataclass
import logging
import re
from unit.log_handler import get_logger
from interface.application import BaseInterface
from interface.application import CPU
from interface.application import System

logger = get_logger(__name__, logging.INFO)


class BaseOS(ABC):
    '''docstring'''
    def __init__(self, interface: BaseInterface):
        self.api = interface
        self._cpu = None
        self._logic_processors = None
        self._mac_address = None
        self.memory_size = self._get_memory_size()
        self._system = None

    @abstractmethod
    def _get_memory_size(self) -> int:
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
            version: System manufacturer
            serial: Used for indentifying system
    '''
    def __init__(self, interface: BaseInterface):
        self.api = interface
        # self.vendor, self.model, self.name = self._get_system_info().values()
        self.nic_name = interface.if_name
        self.memory_size = self._get_memory_size()
        self.error_features = defaultdict(set)

    @property
    def logic_processors(self) -> int:
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
            cpus = self.api.command_line.original(
                self.api,
                'wmic cpu Get NumberOfCores,NumberOfLogicalProcessors '
                '/Format:List'
            )
            logger.debug('cpus = %s', cpus)
            output_string = "".join(cpus)
            logger.debug('output_string = %s', output_string)
            match = re.search(r'NumberOfLogicalProcessors=(\d+)',
                              output_string)

            if match:
                self._logic_processors = int(match.group(1))
                logger.debug("logic_processor = %d",
                             self._logic_processors)
            else:
                raise ValueError("No matching logical processor found.")
            return self._logic_processors

        except re.error as e:
            logger.error("Invalid regex pattern: %s", e)
            raise
        except Exception as e:
            logger.error('_get_hyperthreading: %s', e)
            raise

    def _get_memory_size(self) -> int:
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
    def mac_address(self) -> str:
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

    def _get_system_info(self) -> dict[str]:
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

    @property
    def cpu(self) -> CPU:
        ''' Get CPU information
            Grep CPU information from system call 'lscpu'
            Args: None
            Returns: A dictionary consists of CPU(s) and Model Name
            Raises: Logger error
        '''
        try:
            wmic_manufacturer: str = self.api.command_line(
                "wmic cpu get Manufacturer")
            cpu_manufacturer: str = wmic_manufacturer.get(1).split(" ")[0]
            wmic_cores: str = self.api.command_line(
                "wmic cpu get NumberOfCores")
            cpu_cores: int = int(wmic_cores.get(1).split(" ")[0])
            wmic_name: str = self.api.command_line("wmic cpu get name")
            cpu_name: str = " ".join(wmic_name.get(1).split(" ")[0:3])
            logger.debug("cpu_cores = %d, cpu_name = %s", cpu_cores,
                         cpu_name)
            self._cpu = CPU(
                vendor=cpu_manufacturer,
                model=cpu_name,
                hyperthreading=(self.logic_processors/cpu_cores == 2),
                cores=cpu_cores
            )
        except ValueError as e:
            logger.error("Value Error in get_cpu_info: %s", e)
            raise
        except Exception as e:
            logger.error('error occurred in get_cpu_info: %s', e)
            raise
        return self._cpu

    @property
    def system(self) -> System:
        ''' Get Desktop Computer information
            Grep HW information from system call 'lshw'
            Args: None
            Returns: A dictionary consists of Version and Serial
            Raises: Logger error
        '''
        try:
            computer_info: str = self.api.command_line(
                'wmic computersystem get Name, Manufacturer, Model')

            baseboard_info: str = self.api.command_line(
                'wmic baseboard get Version')

            memory_info = self.api.command_line(
                'wmic ComputerSystem get TotalPhysicalMemory')

            if (computer_info and len(computer_info) > 1 and memory_info
                    and len(memory_info) > 1):
                self._system = System(
                    manufacturer=(
                        ' '.join(computer_info.get(1).split(' ')[0:1])
                    ),
                    model=' '.join(computer_info.get(1).split(' ')[2:4]),
                    name=computer_info.get(1).split(' ')[5].lstrip(),
                    rev=baseboard_info.get(1).split(' ')[1],
                    memory=f"{int(memory_info.get(1))//(1024 ** 3)} GB"
                )
            else:
                raise ValueError("Failed to get system info.")
            logger.debug('manufacturer = %s', self._system.manufacturer)
            logger.debug('model = %s', self._system.model)
            logger.debug('name = %s', self._system.name)
            logger.debug('rev = %s', self._system.rev)
            logger.debug('memory = %s', self._system.memory)

        except Exception as e:
            logger.error('Error occurred in _get_desktop_info: %s', e)
            raise
        return self._system


class AMD64Linux(BaseOS):
    '''docstring'''
    def _get_memory_size(self):
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
