# Contents of amd_64_nvme.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
import logging
import os
# import paramiko
import re
import pandas as pd
# import time
from amd_desktop.win10_interface import Win10Interface as win10
from unit.system_under_testing import convert_size
from unit.system_under_testing import dict_to_dataframe
# from unit.system_under_testing import RasperberryPi as rpi
# import psutil

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(filename='C:\paramiko.log')
logger = logging.getLogger(__name__)
# logger = logging.getLogger("paramiko")

class AMD64NVMe(object):
    ''' AMD 64 NVMe System
        Any operations of the system that are not included in the DUT behavior

        Attributes:
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
    def __init__(self, str_manufacturer: str, nic_name):
        # self.api = win10('remote', 'eth0', f'{str_manufacturer}.json')
        self.api = win10()
        self.os = self.api.get_os()
        self.manufacturer = str_manufacturer
        self.vid, self.did, self.sdid, self.rev = self._get_pcie_info().values()
        self.cpu_num, self.cpu_name = self._get_cpu_info().values()
        self.vendor, self.model, self.name = self._get_desktop_info().values()
        self.disk_num, self.serial_num = self._get_disk_num().values()
        self.volume, self.size = self._get_volume().values()
        self.nic_name = nic_name
        self._mac_address = None
    
    @property
    def mac_address(self):
        ''' Get MAC address
            Parse MAC address from power shell 'Get-NetAdapter'
            Args: None
            Returns: Attribute _mac_address
            Raises: Value
        '''
        if hasattr(self, '_mac_address') and self._mac_address:
            return self._mac_address

        try:
            output = self.api.command_line('powershell Get-NetAdapter')
            logger.debug(f'output = {output}')

            filtered = output.get(3)
            logger.debug(f'filtered = {filtered}')
            if not filtered:
                raise ValueError(
                    "Failed to retrieve the expected output from command.")
        
            match = re.search(r"Ethernet 7\s+.*?\s+([A-F0-9-]{17})\s", filtered)
            if match:
                mac_address = match.group(1)
                logger.debug(f"Found: {mac_address}")
                self._mac_address = mac_address
            else:
                raise ValueError("No matching Ethernet adapter found.")
            
        except (ValueError, Exception) as e:
            logger.error(f'Error: {e}')
            self._mac_address = None

        return self._mac_address

    def _get_cpu_info(self) -> dict[str, str]:
        ''' Get CPU information
            Grep CPU information from system call 'lscpu'
            Args: None
            Returns: A dictionary consists of CPU(s) and Model Name
            Raises: Logger error
        '''
        str_return = int_cpu_num = str_cpu_name = None
        try:
            str_return = self.api.command_line('wmic cpu get NumberOfCores')
            int_cpu_num = int(str_return.get(1).split(' ')[0])
            str_return = self.api.command_line('wmic cpu get name')
            # str_cpu_num = str_return.get(1).split(' ')[4]
            str_cpu_name = ' '.join(str_return.get(1).split(' ')[0:3])
            logger.debug('cpu_num = %d, cpu_name = %s',
                         int_cpu_num, str_cpu_name)
        except Exception as e:
            logger.error('error occurred in _get_cpu_info: %s', e)
        
        return {"CPU(s)": int_cpu_num, "Model Name": str_cpu_name}

    def _get_disk_num(self):
        try:
            str_return = int_disk_num = None
            if self.manufacturer == "VEN_1B4B":
                str_target = "Marvell"
            else:
                str_target = "CT500P5SSD8"
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
        # finally:
            # return int(str_disk_num)
        return {"Number": int_disk_num, "SerialNumber": str_serial_num}
            

    def _get_desktop_info(self) -> dict[str, str]:
        ''' Get Desktop Computer information
            Grep HW information from system call 'lshw'
            Args: None
            Returns: A dictionary consists of Version and Serial
            Raises: Logger error
        '''
        str_return = str_version = str_serial = None
        try:
            # str_return = self.api.command_line('lshw|grep "Desktop" -A 4CA')
            str_return = self.api.command_line(
                'wmic computersystem get Name, Manufacturer, Model')
            str_vendor = ' '.join(str_return.get(1).split(' ')[0:1])
            str_model = ' '.join(str_return.get(1).split(' ')[2:4])
            str_name = str_return.get(1).split(' ')[5].lstrip()
            logger.debug('vendor = %s', str_vendor)
            logger.debug('model = %s', str_model)
            logger.debug('name = %s', str_name)
    
        except Exception as e:
            logger.error('Error occurred in _get_desktop_info: %s', e)
        # finally:
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
        str_return = str_bdf = str_sdid = None
        try:
            str_return = self.api.command_line(
                f"wmic path win32_pnpentity get deviceid, name|findstr {self.manufacturer}")
            logger.debug('__dict_return = %s', str_return)
            
            # Check if str_return is None
            if str_return is None:
                raise ValueError("Received None from command_line")
            
            pattern = r"VEN_(\w+)&DEV_(\w+)&SUBSYS_(\w+)&REV_(\w+)"
            match = re.search(pattern, str_return.get(0))
            if match:
                str_vid, str_did, str_sdid, str_rev = match.groups()
            logger.debug(
                    'manufacturer = %s, vid = %s, did = %s',
                    self.manufacturer, str_vid, str_did)
            logger.debug('sdid = %s, rev = %s', str_sdid, str_rev)
                   
        except Exception as e:
            logger.error('Error occurred in _get_pcie_info: %s', e)
            raise
        # finally:
            # return {"BDF": str_bdf, "SDID": str_sdid}
        return {"VID": str_vid, "DID": str_sdid,
                "SDID": str_sdid, "Rev": str_rev}

    def _get_volume(self):
        ''' Get Volume
            Args: None
            Returns: Volume, Size
            Raises: Any errors
        '''
        try:
            str_return = self.api.command_line(
                    f"powershell Get-Partition -DiskNumber {self.disk_num}")
            str_volume = str_return.get(7).split(' ')[1]
            # str_size = ' '.join(str_return.get(7).split(' ')[3:5])
            logger.debug('volume = %s', str_volume)
            # logger.debug('size = %s', str_size)
        except Exception as e:
            logger.error('Error occurred in _get_volume: %s', e)
            raise
        else:
            if str_volume:
                str_size = ' '.join(str_return.get(7).split(' ')[3:5])
                logger.debug('size = %s', str_size)
            else:
                raise ValueError("Unexpected None value returned")
        finally:
            return {
                    "Volume": str_volume,
                    "Type": str_size
                    }

    # def run_io_operation(self, thread: int, iodepth: int, block_size: str,
    #     random_size: str, write_pattern: int, duration: int, io_file: str) ->\
    #     dict[str, str | int]:
    #     ''' Run DISKSPD
    #         Args:
    #             thread 2 -t2
    #             iodepth 32 -o32
    #             blocksize 4k -b4k
    #             random 4k -r4k
    #             write 0% -w0
    #             duration 120 seconds -d120
    #             writethrough -Sh
    #             data ms -D
    #             5GB test file -c5g
    #         Returns: read bw, read iops, write bw, write iops
    #         Raises: Any errors occurs while invoking diskspd
    #     '''
    #     read_iops = read_bw = write_iops = write_bw = None
    #     try:
    #         if random_size:
    #             str_command = f'diskspd -t{thread} -o{iodepth} -b{block_size} \
    #                 -r{random_size} -w{write_pattern} -d{duration} -Sh -D -c5g {io_file}'
    #         else:
    #             str_command = f'diskspd -t{thread} -o{iodepth} -b{block_size} \
    #                 -w{write_pattern} -d{duration} -Sh -D -c5g {io_file}'
            
    #         str_output = self.api.io_command(str_command)
    #         # logger.debug('str_output = %s', str_output)
            
    #         read_io_section = re.search(r'Read IO(.*?)Write IO', str_output, re.S)
    #         write_io_section = re.search(r'Write IO(.*?)(\n\n|\Z)', str_output, re.S)
    #         # logger.debug(f'write_io_section = {write_io_section.group(1)}')

    #         if read_io_section:
    #             read_io_text = read_io_section.group(1)

    #             # Extract total and I/O per s values
    #             read_pattern = re.compile(r'total:\s*([\d\s|.]+)')
    #             read_match = read_pattern.search(read_io_text)

    #             if read_match:
    #                 read_values = read_match.group(1).split('|')
    #                 read_iops = read_values[3].strip()
    #                 read_bw = read_values[2].strip()
    #                 logger.debug('read_iops = %s', read_iops)
    #                 logger.debug('read_bw = %s', read_bw)

    #         if write_io_section:
    #             write_io_text = write_io_section.group(1)

    #             # Extract total and I/O per s value
    #             write_pattern = re.compile(r'total:\s*([\d\s|.]+)')
    #             write_match = write_pattern.search(write_io_text)
    #             if write_match:
    #                 write_values = write_match.group(1).split('|')
    #                 write_iops = write_values[3].strip()
    #                 write_bw = write_values[2].strip()
    #                 logger.debug('write_iops = %s', write_iops)
    #                 logger.debug('write_bw = %s', write_bw)

    #     except Exception as e:
    #         logger.error(f"Error occurred in run_io_operation: {e}")
    #         raise
    #     finally:
    #         return float(read_bw), float(read_iops), float(write_bw), float(write_iops)

