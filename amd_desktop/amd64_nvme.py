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
logger = logging.getLogger(__name__)


class AMD64NMMe(object):
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
    def __init__(self, str_manufacturer: str):
        self.api = win10('remote', 'eth0', 'app_map.json')
        self.os = self.api.get_os()
        self.manufacturer = str_manufacturer
        self.vid, self.did, self.sdid, self.rev = self._get_pcie_info().values()
        self.cpu_num, self.cpu_name = self._get_cpu_info().values()
        self.vendor, self.model, self.name = self._get_desktop_info().values()
        self.disk_num, self.serial_num = self._get_disk_num().values()
        self.volume, self.size = self._get_volume().values()

    def _get_cpu_info(self) -> dict[str, str]:
        ''' Get CPU information
            Grep CPU information from system call 'lscpu'
            Args: None
            Returns: A dictionary consists of CPU(s) and Model Name
            Raises: Logger error
        '''
        str_return = str_cpu_num = str_cpu_name = None
        try:
            str_return = self.api.command_line('wmic cpu get name')
            str_cpu_num = str_return.get(1).split(' ')[4]
            str_cpu_name = ' '.join(str_return.get(1).split(' ')[0:3])
            logger.debug('str_cpu_num = %s, str_cpu_name = %s',
                         str_cpu_num, str_cpu_name)
        except Exception as e:
            logger.error('error occurred in _get_cpu_info: %s', e)
        finally:
            return {"CPU(s)": str_cpu_num, "Model Name": str_cpu_name}

    def _get_disk_num(self):
        try:
            str_return = int_disk_num = None
            str_return = self.api.command_line(
                f'powershell Get-PhysicalDisk|findstr {self.manufacturer}')
            logger.debug('str_return = %s', str_return)
            
            # Check if str_return is None
            if str_return is None:
                raise ValueError("Received None from command_line")
            
            int_disk_num = int(str_return.get(0).split(' ')[0].lstrip())
            str_serial_num = str_return.get(0).split(' ')[2].lstrip()
            logger.debug('int_disk_num = %d', int_disk_num)
            logger.debug('str_serial_num = %s', str_serial_num)
            
        except Exception as e:
            logger.error('Error occurred in _get_disk_num: %s', e)
            raise
        finally:
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
            logger.debug('str_vendor = %s', str_vendor)
            logger.debug('str_model = %s', str_model)
            logger.debug('str_name = %s', str_name)
    
        except Exception as e:
            logger.error('Error occurred in _get_desktop_info: %s', e)
        finally:
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
            match = re.search(pattern, str_return.get(1))
            if match:
                str_vid, str_did, str_sdid, str_rev = match.groups()
            logger.debug(
                    'self.manufacturer = %s, str_vid = %s, str_did = %s',
                    self.manufacturer, str_vid, str_did)
            logger.debug('str_sdid = %s, str_rev = %s', str_sdid, str_rev)
                   
        except Exception as e:
            logger.error('Error occurred in _get_pcie_info: %s', e)
            raise
        finally:
            # return {"BDF": str_bdf, "SDID": str_sdid}
            return {"VID": str_vid, "DID": str_sdid,
                    "SDID": str_sdid, "Rev": str_rev}

    @dict_to_dataframe
    @convert_size
    def run_io_operation(
                self,
                str_rw: str,
                str_bs: str,
                str_iodepth: str,
                str_numjobs: str,
                str_runtime: str,
                int_cpumask: int) -> dict[str, str | int]:
        ''' Run FIO
            Args:
            Returns:
            Raises:
        '''
        bool_return = str_iops_temp = str_iops = str_bw_temp = str_bw = None
        try:
            bool_return = self.api.io_command(f'diskspd --filename=/dev/{self.node} \
                    --direct=1 --rw={str_rw} --bs={str_bs} --ioengine=libaio \
                    --iodepth={str_iodepth} --runtime={str_runtime} \
                    --numjobs={str_numjobs} --time_based --group_reporting \
                    --name=iops-test-job --eta-newline=1 \
                    --cpumask={int_cpumask} | tee iops.log')
            logger.debug('_bool_return = %s', bool_return)
            if str_rw == 'randread' or str_rw == 'read':
                dict_return = \
                    self.api.command_line("cat ~/iops.log | grep 'read:'")
            if str_rw == 'randwrite' or str_rw == 'write':
                dict_return = \
                    self.api.command_line('cat ~/iops.log | grep "write:"')
            if str_rw == 'randrw':
                dict_return = \
                    self.api.command_line('cat ~/iops.log | grep "write:"')
            str_iops_temp = dict_return.get(0).split(':')[1]
            str_iops = str_iops_temp.split('=')[1].split(',')[0]
            str_bw_temp = dict_return.get(0).split(':')[1].split('=')[2]
            str_bw = str_bw_temp.split(',')[0].split(' ')[0]
            logger.debug('str_iops = %s, str_bw = %s', str_iops, str_bw)
        except Exception as e:
            logger.error(f"Error occurred in _get_nvme_smart_log: {e}")
            raise
        finally:
            return {
                    "IOPS": str_iops,
                    "BW": str_bw,
                    "File Name": self.node,
                    "RW Mode": str_rw,
                    "Block Size": str_bs,
                    "IO Depth": str_iodepth,
                    "Job": str_numjobs,
                    "Run Time": str_runtime,
                    "CPU Mask": int_cpumask
                    }

    def _get_volume(self):
        str_return = self.api.command_line(
                f"powershell Get-Partition -DiskNumber {self.disk_num}")
        str_volume = str_return.get(7).split(' ')[1]
        str_size = ' '.join(str_return.get(7).split(' ')[3:5])
        logger.debug('str_volume = %s', str_volume)
        logger.debug('str_size = %s', str_size)
        return {
                "Volume": str_volume,
                "Type": str_size
                }
                
        # disk_partitions = psutil.disk_partitions(all=True)
        # result = {}

        # for partition in disk_partitions:
        #     print(f"partition.device = {partition.device}")
        #     try:
        #         disk_usage = psutil.disk_usage(partition.mountpoint)
        #         # 检查设备名称是否包含物理磁盘编号
        #         # if f"PhysicalDrive{self.disk_num}" in partition.device:
        #         if f"PhysicalDrive0" in partition.device:
        #             print('Bingo!!!!!!!!!!!!!!!!')
        #             result[partition.device] = {
        #                 "Mountpoint": partition.mountpoint,
        #                 "File system type": partition.fstype,
        #                 "Total size": disk_usage.total,
        #                 "Used": disk_usage.used,
        #                 "Free": disk_usage.free,
        #                 "Percentage": disk_usage.percent
        #             }
        #             print(f"partition.mountpoint = {partition.mountpoint}")
        #     except PermissionError:
        #         # 处理无访问权限的分区
        #         continue
        
        # return result
