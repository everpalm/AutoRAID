# Contents of system_under_testing.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
import logging
import os
# import paramiko
import re
# import pandas as pd
# import time
from unit.application_interface import ApplicationInterface as api

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def convert_size(callback):
    ''' Convert string that includes a number and unit in a dictionary
        e.g. convert 19.6k to 19.6 * 1024 = 20070.4
        Args: Dictionary
        Returns: Floats in a dictionary
        Raises: None
    '''
    def wrapper(*args, **kwargs):
        str_result = callback(*args, **kwargs)
        logger.debug(
                "Typte = %s, data to be converted = %s",
                type(str_result),
                str_result)
        pattern = r'(\d+(?:\.\d+)?)\D*([kKmMgG])'
        for key, value in str_result.items():
            logger.debug('key = %s, value = %s', key, value)
            # Only process IOPS and BW
            if key == 'IOPS' or key == 'BW':
                if value == 0:
                    continue
                match = re.search(pattern, value)
                logger.debug("match = %s", match)
                if match:
                    num = match.group(1)
                    unit = match.group(2)
                    logger.debug("num = %s, unit = %s", num, unit)
                    num = float(num)
                    if unit == 'K' or unit == 'k':
                        factor = 1024
                    elif unit == 'M':
                        factor = 1048576
                    elif unit == 'G':
                        factor = 1073741824
                    elif unit == 'T':
                        factor = 1099511627776
                    str_result[key] = num * factor
                else:
                    # pass
                    str_result[key] = float(value)
        return str_result
    return wrapper


# def dict_to_dataframe(callback):
#     ''' Convert a dictionary to a Pandas dataframe
#         Args: Any dictionary
#         Returns: A dataframe
#         Raises: ValueError, IOError
#     '''
#     def wrapper(*args, **kwargs):
#         result_dict = callback(*args, **kwargs)
#         if isinstance(result_dict, dict):
#             df = pd.DataFrame([result_dict], index=[0])
#             logger.debug("df = %s", df)
#             try:
#                 if os.path.exists('my_data.json'):
#                     existing_data = pd.read_json('my_data.json',
#                                                  orient='records',
#                                                  lines=True)
#                     combined_data = pd.concat([existing_data, df],
#                                               ignore_index=True)
#                 else:
#                     combined_data = df
#                 combined_data.to_json('my_data.json',
#                                       orient='records',
#                                       lines=True)
#             except IOError as e:
#                 logger.error(f"Error occurred in dict_to_dataframe: {e}")
#                 raise
#             return df
#         else:
#             raise ValueError("Input is not a dictionary!")
#     return wrapper


class RaspberryPi(object):
    ''' Raspberry Pi
        Any operations associated with Rasperberry Pi

        API:
            mode: local
            network interface: eth0
            config file: app_map.json
    '''
    def __init__(self, str_uart_path, int_baut_rate, str_file_name):
        self.uart_path = str_uart_path
        self.baut_rate = int_baut_rate
        self.file_name = str_file_name
        self.api = api('local', 'eth0', 'app_map.json')

    def open_uart(self):
        logger.debug('self.file_name = %s', self.file_name)
        self.api.command_line(f"sudo screen -dm -L -Logfile {self.file_name}"
                          f" {self.uart_path} {self.baut_rate}")

    def close_uart(self) -> int:
        str_return = self.api.command_line("sudo screen -ls")
        logger.debug('str_return = %s', str_return)
        int_uart_port = str_return.get(1).split('..')[0]
        logger.info('int_uart_port is %d', int(int_uart_port))
        self.api.command_line(f"sudo screen -X -S {int_uart_port} quit")
        return int_uart_port


class SystemUnderTesting(api):
    ''' System Under Testing

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
        super().__init__(
                str_mode='remote',
                str_if_name='eth0',
                str_config_file='app_map.json')
        self.os = self.get_os()
        self.manufacturer = str_manufacturer
        self.bdf, self.sdid = self._get_pcie_info().values()
        self.node, self.sn, self.model, self.namespace_id, \
            self.namespace_usage, self.fw_rev = \
            self._get_nvme_device().values()
        self.critical_warning, self.temperature, self.power_cycles, \
            self.unsafe_shutdowns = self._get_nvme_smart_log().values()
        self.cpu_num, self.cpu_name = self._get_cpu_info().values()
        self.version, self.serial = self._get_desktop_info().values()

    def _get_cpu_info(self) -> dict[str, str]:
        ''' Get CPU information
            Grep CPU information from system call 'lscpu'
            Args: None
            Returns: A dictionary consists of CPU(s) and Model Name
            Raises: Logger error
        '''
        str_return = str_cpu_num = str_cpu_name = None
        try:
            str_return = self.command_line('lscpu|grep "CPU"')
            str_cpu_num = str_return.get(1).split(' ')[1]
            str_cpu_name = str_return.get(4).split(':')[1].lstrip()
            logger.debug('str_cpu_num = %s, str_cpu_name = %s',
                         str_cpu_num, str_cpu_name)
        except Exception as e:
            logger.error('error occurred in _get_cpu_info: %s', e)
            raise
        # finally:
        return {"CPU(s)": str_cpu_num, "Model Name": str_cpu_name}

    def _get_desktop_info(self) -> dict[str, str]:
        ''' Get Desktop Computer information
            Grep HW information from system call 'lshw'
            Args: None
            Returns: A dictionary consists of Version and Serial
            Raises: Logger error
        '''
        str_return = str_version = str_serial = None
        try:
            str_return = self.command_line('lshw|grep "Desktop" -A 4')
            str_version = str_return.get(3).split(':')[1].lstrip()
            str_serial = str_return.get(4).split(':')[1].lstrip()
        except Exception as e:
            logger.error('Error occurred in _get_desktop_info: %s', e)
            raise
        finally:
            return {"Version": str_version, "Serial": str_serial}

    def _get_pcie_info(self) -> dict[str, str]:
        ''' Get PCIe information
            Grep manufactuer HW IDs from system call 'lspci -v'
            Args: None
            Returns: A dictionary consists of BDF and SDID
            Raises: None
        '''
        str_return = str_bdf = str_sdid = None
        try:
            str_return = self.command_line(
                f"lspci -v|grep {self.manufacturer}")
            logger.debug('__dict_return = %s', str_return)
            str_bdf = str_return.get(0).split(' ')[0]
            str_sdid = str_return.get(1).split(' ')[-1]
            logger.debug(
                    'self.manufacturer = %s, str_bdf = %s, self.bdf = %s',
                    self.manufacturer,
                    str_bdf, str_sdid)
        except Exception as e:
            logger.error('Error occurred in _get_pcie_info: %s', e)
            raise
        finally:
            return {"BDF": str_bdf, "SDID": str_sdid}

    @staticmethod
    def get_os() -> str:
        ''' Get OS version
            Args: None
            Returns: OS type
            Raises: None
        '''
        if os.name == 'nt':
            str_msg = 'Windows'
        elif os.name == 'posix':
            str_msg = 'Linux'
        else:
            str_msg = 'Unknown'
        logger.debug('str_msg = %s', str_msg)
        return str_msg

    def _get_nvme_device(self) -> dict[str, str]:
        ''' Get NVMe device name
            Args:
            Returns:
            Raises:
        '''
        str_node = str_sn = str_model = str_namespace_id = str_namespace_usage\
            = str_fw_rev = None
        try:
            str_return = self.command_line("nvme list|grep /dev/nvme")
            logger.debug('str_return = %s', str_return)
            str_node = str_return.get(0).split(' ')[0].split('/')[2]
            str_sn = str_return.get(0).split(' ')[1]
            str_model = str_return.get(0).split(' ')[2]
            str_namespace_id = str_return.get(0).split(' ')[3]
            str_namespace_usage = str_return.get(0).split(' ')[4] + ' ' + \
                str_return.get(0).split(' ')[5]
            str_fw_rev = str_return.get(0).split(' ')[-1]
            logger.debug(
                    'str_node = %s, str_sn = %s, str_model = %s, \
                        str_namespace_id = %s, str_namespace_usage = %s,\
                            str_fw_rev = %s',
                    str_node,
                    str_sn,
                    str_model,
                    str_namespace_id,
                    str_namespace_usage,
                    str_fw_rev)
        except Exception as e:
            logger.error(f"Error occurred in _get_nvme_device: {e}")
            raise
        finally:
            return {
                    "Node": str_node,
                    "SN": str_sn,
                    "Model": str_model,
                    "Namespace ID": str_namespace_id,
                    "Namespace Usage": str_namespace_usage,
                    "FW Rev": str_fw_rev
                    }

    def _get_nvme_smart_log(self) -> dict[str, int]:
        ''' Get NVMe SMART log
            Args:
            Returns:
            Raises:
        '''
        dict_return = int_critical_warning = int_temperature = \
            int_power_cycles = int_unsafe_shutdowns = None
        try:
            dict_return = self.command_line(
                    f'nvme smart-log /dev/{self.node}')
            int_critical_warning = int(dict_return.get(1).split(':')[1])
            int_temperature = int(dict_return.get(2).split(' ')[2])
            int_power_cycles = int(dict_return.get(11).split(':')[1])
            int_unsafe_shutdowns = int(dict_return.get(13).split(':')[1])
            logger.debug(
                    'int_critical_warning = %s , int_temperature = %s,\
                        int_power_cycles = %s, int_unsafe_shutdowns = %s',
                    int_critical_warning,
                    int_temperature,
                    int_power_cycles,
                    int_unsafe_shutdowns)
        except ValueError as ve:
            logger.error(f"Value error occurred in _get_nvme_smart_log: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error occurred in _get_nvme_smart_log: {e}")
            raise
        finally:
            return {
                    "critical_warning": int_critical_warning,
                    "temperature": int_temperature,
                    "power_cycles": int_power_cycles,
                    "unsafe_shutdowns": int_unsafe_shutdowns
                    }

    # @dict_to_dataframe
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
            bool_return = self.io_command(f'fio --filename=/dev/{self.node} \
                    --direct=1 --rw={str_rw} --bs={str_bs} --ioengine=libaio \
                    --iodepth={str_iodepth} --runtime={str_runtime} \
                    --numjobs={str_numjobs} --time_based --group_reporting \
                    --name=iops-test-job --eta-newline=1 \
                    --cpumask={int_cpumask} | tee iops.log')
            logger.debug('_bool_return = %s', bool_return)
            if str_rw == 'randread' or str_rw == 'read':
                dict_return = \
                    self.command_line("cat ~/iops.log | grep 'read:'")
            if str_rw == 'randwrite' or str_rw == 'write':
                dict_return = \
                    self.command_line('cat ~/iops.log | grep "write:"')
            if str_rw == 'randrw':
                dict_return = \
                    self.command_line('cat ~/iops.log | grep "write:"')
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