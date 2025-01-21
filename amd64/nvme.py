# Contents of amd64/nvme.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from collections import defaultdict
import logging
# import math
import re
from unit.log_handler import get_logger
from interface.application_interface import GenericAPI
# import os

logger = get_logger(__name__, logging.INFO)


class AMD64NVMe:
    ''' AMD 64 NVMe System
        Any operations of the system that are not included in the DUT behavior

        Attributes:
            interface: Pass object with the 1st argument
            os: Operation System
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
    def __init__(self, interface: GenericAPI):
        self.api = interface
        self.os = self.api.get_os()
        self.manufacturer = interface.config_file.replace('.json', '')
        self.vid, self.did, self.sdid, self.rev = \
            self._get_pcie_info().values()
        self.cpu_num, self.cpu_name = self.get_cpu_info().values()
        self.vendor, self.model, self.name = self._get_desktop_info().values()
        self.nic_name = interface.if_name
        self._mac_address = None
        self.memory_size = self._get_memory_size()
        self.hyperthreading = self._get_hyperthreading()
        self.error_features = defaultdict(set)

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

            # match = re.search(r"Ethernet 7\s+.*?\s+([A-F0-9-]{17})\s",
            #                   filtered)
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
