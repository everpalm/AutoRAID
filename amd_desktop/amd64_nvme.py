# Contents of amd_64_nvme.py
"""Copyright (c) 2024 Jaron Cheng"""
from __future__ import annotations  # Header, Python 3.7 or later version
from collections import defaultdict
import logging

# import os
import re

# from unit.system_under_testing import convert_size


logger = logging.getLogger(__name__)


class AMD64NVMe:
    """AMD 64 NVMe System
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
    """

    def __init__(self, interface):
        self.api = interface
        self.os = self.api.get_os()
        self.manufacturer = interface.config_file.replace(".json", "")
        self.vid, self.did, self.sdid, self.rev = self._get_pcie_info().values()
        self.cpu_num, self.cpu_name = self.get_cpu_info().values()
        self.vendor, self.model, self.name = self._get_desktop_info().values()
        self.disk_num, self.serial_num = self._get_disk_num().values()
        self.disk_info = self._get_volume()
        self.nic_name = interface.if_name
        self._mac_address = None
        self.memory_size = self._get_memory_size()
        self.hyperthreading = self._get_hyperthreading()
        self.error_features = defaultdict(set)

    def _get_hyperthreading(self):
        '''This is a docstring'''
        try:
            output = self.api.command_line._original(
                self.api,
                "wmic cpu Get NumberOfCores,NumberOfLogicalProcessors /Format:List",
            )
            logger.debug("output = %s", output)
            output_string = "".join(output)
            logger.debug("output_string = %s", output_string)
            match = re.search(r"NumberOfLogicalProcessors=(\d+)", output_string)

            if match:
                int_logical_processor = int(match.group(1))
                logger.debug("int_logical_processor = %d", int_logical_processor)
            else:
                raise ValueError("No matching logical processor found.")
            if int_logical_processor / self.cpu_num == 2:
                return True
        except ValueError as e:
            logger.error("Value Error in _get_hyperthreading: %s", e)
        except Exception as e:
            logger.error("Unexpected error in _get_hyperthreading: %s", e)
            raise
        return False

    def _get_memory_size(self):
        '''This is a docstring'''
        try:
            dict_memory_size = self.api.command_line(
                "wmic ComputerSystem get TotalPhysicalMemory"
            )
            logger.debug("dict_memory_size = %s", dict_memory_size)
            int_memory_size = int(dict_memory_size.get(1)) // (1024**3)
            logger.debug("int_memory_size = %s", int_memory_size)
        except ValueError as e:
            logger.error("Value Error in _get_memory_size: %s", e)
        except Exception as e:
            logger.error("Unexpected error in _get_memory_size: %s", e)
            raise
        return int_memory_size

    @property
    def mac_address(self):
        """Get MAC address
        Parse MAC address from power shell 'Get-NetAdapter'
        Args: None
        Returns: Attribute _mac_address
        Raises: Value
        """
        if hasattr(self, "_mac_address") and self._mac_address:
            return self._mac_address

        try:
            output = self.api.command_line("powershell Get-NetAdapter")
            logger.debug("output = %s", output)

            filtered = output.get(3)
            logger.debug("filtered = %s", filtered)
            if not filtered:
                raise ValueError("Failed to retrieve the expected output from command.")

            match = re.search(r"Ethernet 7\s+.*?\s+([A-F0-9-]{17})\s", filtered)
            if match:
                mac_address = match.group(1)
                logger.debug("Found: %s", mac_address)
                self._mac_address = mac_address
            else:
                raise ValueError("No matching Ethernet adapter found.")
        except AttributeError as e:
            logger.error("AttributeError in mac_address: %s", e)
        except re.error as e:
            logger.error("Invalid regex pattern in mac_address: %s", e)
            return False
        except Exception as e:
            logger.error("An unexpected error in mac_address: %s", e)
            self._mac_address = None

        return self._mac_address

    def get_cpu_info(self) -> dict[str, str]:
        """Get CPU information
        Grep CPU information from system call 'lscpu'
        Args: None
        Returns: A dictionary consists of CPU(s) and Model Name
        Raises: Logger error
        """
        str_return = int_cpu_num = str_cpu_name = None
        try:
            str_return = self.api.command_line("wmic cpu get NumberOfCores")
            int_cpu_num = int(str_return.get(1).split(" ")[0])
            str_return = self.api.command_line("wmic cpu get name")
            str_cpu_name = " ".join(str_return.get(1).split(" ")[0:3])
            logger.debug("cpu_num = %d, cpu_name = %s", int_cpu_num, str_cpu_name)
        except ValueError as e:
            logger.error("Value Error in get_cpu_info: %s", e)
        except Exception as e:
            logger.error("Unexpected error occurred in get_cpu_info: %s", e)

        return {"CPU(s)": int_cpu_num, "Model Name": str_cpu_name}

    def _get_disk_num(self):
        '''This is a docstring'''
        try:
            str_return = int_disk_num = None
            if self.manufacturer == "VEN_1B4B":
                str_target = "Marvell"
            else:
                str_target = "CT500P5SSD8"
            str_return = self.api.command_line(
                f"powershell Get-PhysicalDisk|findstr {str_target}"
            )
            logger.debug("str_return = %s", str_return)

            # Check if str_return is None
            if str_return is None:
                raise ValueError("Received None from command_line")

            int_disk_num = int(str_return.get(0).split(" ")[0].lstrip())
            str_serial_num = str_return.get(0).split(" ")[2].lstrip()
            logger.debug("disk_num = %d", int_disk_num)
            logger.debug("serial_num = %s", str_serial_num)
        except ValueError as e:
            logger.error("Value Error in _get_disk_num: %s", e)
        except Exception as e:
            logger.error("Error occurred in _get_disk_num: %s", e)
            raise
        return {"Number": int_disk_num, "SerialNumber": str_serial_num}

    def _get_desktop_info(self) -> dict[str, str]:
        """Get Desktop Computer information
        Grep HW information from system call 'lshw'
        Args: None
        Returns: A dictionary consists of Version and Serial
        Raises: Logger error
        """
        str_return = str_vendor = str_model = str_name = None
        try:
            # str_return = self.api.command_line('lshw|grep "Desktop" -A 4CA')
            str_return = self.api.command_line(
                "wmic computersystem get Name, Manufacturer, Model"
            )
            if str_return:
                str_vendor = " ".join(str_return.get(1).split(" ")[0:1])
                str_model = " ".join(str_return.get(1).split(" ")[2:4])
                str_name = str_return.get(1).split(" ")[5].lstrip()
            else:
                raise ValueError("Failed to get desktop info.")
            logger.debug("vendor = %s", str_vendor)
            logger.debug("model = %s", str_model)
            logger.debug("name = %s", str_name)
        except ValueError as e:
            logger.error("Value Error in _get_desktop_info: %s", e)
        except Exception as e:
            logger.error("Error occurred in _get_desktop_info: %s", e)
        # finally:
        return {"Manufacturer": str_vendor, "Model": str_model, "Name": str_name}

    def _get_pcie_info(self) -> dict[str, str]:
        """Get PCIe information
        Grep manufactuer HW IDs from system call ''
        Args: None
        Returns: A dictionary consists of BDF and SDID
        Raises: None
        """
        str_rev = str_vid = str_did = str_sdid = None
        try:
            dict_return = self.api.command_line(
                f"wmic path win32_pnpentity get deviceid,"
                f" name|findstr {self.manufacturer}"
            )
            logger.debug("dict_return type(%s) = %s", dict_return, dict_return)

            # Check if str_return is None
            if dict_return is None:
                raise ValueError("Received None from command_line")

            pattern = r"VEN_(\w+)&DEV_(\w+)&SUBSYS_(\w+)&REV_(\w+)"
            match = re.search(pattern, dict_return.get(0))
            if match:
                str_vid, str_did, str_sdid, str_rev = match.groups()
            logger.debug(
                "manufacturer = %s, vid = %s, did = %s",
                self.manufacturer,
                str_vid,
                str_did,
            )
            logger.debug("sdid = %s, rev = %s", str_sdid, str_rev)
        except ValueError as e:
            logger.error("Value Error in _get_pcie_info: %s", e)
        except Exception as e:
            logger.error("Device not found: %s", e)
            raise
        return {"VID": str_vid, "DID": str_sdid, "SDID": str_sdid, "Rev": str_rev}

    def _get_volume(self):
        """Get Volume
        Args: None
        Returns: Volume, Size
        Raises: Any errors
        """
        try:
            # 获取命令输出
            str_return = self.api.command_line(
                f"powershell Get-Partition -DiskNumber {self.disk_num}"
            )

            # 使用正则表达式来提取DriveLetter和Size
            pattern = re.compile(r"\d+\s+([A-Z]?)\s+\d+\s+([\d.]+\s+\w+)")

            # 存储结果
            list_disk_info = []

            # 处理命令输出并查找匹配项
            if str_return:
                # 假设 str_return 是一个字典或包含多行字符串的对象，你需要先转换为单一字符串
                if isinstance(str_return, dict):
                    output_string = "\n".join(str_return.values())
                else:
                    output_string = str_return

                for match in pattern.findall(output_string):
                    drive_letter = match[0] if match[0] else "No Drive Letter"
                    size = match[1]
                    list_disk_info.append((drive_letter, size))

                # 使用日志记录器记录统计结果
                total_disks = len(list_disk_info)
                logger.debug("Total number of disks: %d", total_disks)
            else:
                raise ValueError("Unexpected None value returned from command line")
        except ValueError as e:
            logger.error("Value Error in _get_volume: %s", e)
        except Exception as e:
            logger.error("Unexpected error occurred in _get_volume: %s", e)
            raise

        return list_disk_info
