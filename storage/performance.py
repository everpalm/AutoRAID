# Contents of storage/perforamnce.py
'''Copyright (c) 2024 Jaron Cheng'''
import re
import logging
from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Tuple
from interface.application import BaseInterface
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class BasePerf(ABC):
    '''docstring'''
    READ_R_CFL = READ_L_CFL = WRITE_R_CFL = WRITE_L_CFL = None

    def __init__(self, platform, io_file):
        if BasePerf.READ_R_CFL is None:
            BasePerf.READ_R_CFL = 3
        if BasePerf.WRITE_R_CFL is None:
            BasePerf.WRITE_R_CFL = 3
        if BasePerf.READ_L_CFL is None:
            BasePerf.READ_L_CFL = 10
        if BasePerf.WRITE_L_CFL is None:
            BasePerf.WRITE_L_CFL = 7
        self._io_file = io_file
        self._platform = platform
        self._api = platform.api
        self._cpu_num = self._platform.cpu_num
        self._thread = self._cpu_num * 2
        self._file_size = self._platform.memory_size * 2

    @classmethod
    def set_perf_criteria(cls, read_r, write_r, read_l, write_l):
        """
        Sets the perf criteria.

        Args:
            read_r
            write_r
            read_l
            write_l
        """
        cls.READ_R_CFL, cls.WRITE_R_CFL = read_r, write_r
        cls.READ_L_CFL, cls.WRITE_L_CFL = read_l, write_l
        logger.info("Manually set READ_R_CFL: %s", cls.READ_R_CFL)
        logger.info("Manually set WRITE_R_CFL: %s", cls.WRITE_R_CFL)
        logger.info("Manually set READ_L_CFL: %s", cls.READ_L_CFL)
        logger.info("Manually set WRITE_L_CFL: %s", cls.WRITE_L_CFL)

    @abstractmethod
    def run_io_operation(self,
                         iodepth: int,
                         block_size: str,
                         random_size: Optional[str],
                         write_pattern: str,
                         duration: int) -> Tuple[float, float, float, float]:
        pass


class WindowsPerf(BasePerf):
    '''Windows Performance
    Args:
        platform: Operation system plus barebone
        io_file: File/block device
    '''
    def run_io_operation(self,
                         iodepth: int,
                         block_size: str,
                         random_size: Optional[str],
                         write_pattern: str,
                         duration: int) -> Tuple[float, float, float, float]:
        ''' Run DISKSPD
            Args:
                iodepth: IO深度
                block_size: 塊大小
                random_size: 隨機大小（可選）
                write_pattern: 寫入模式百分比
                duration: 測試持續時間（秒）
            Returns: read bw, read iops, write bw, write iops
            Raises: 執行過程中的任何異常
        '''
        logger.info("Thread count = %s", self._thread)
        logger.info("IO depth = %s", iodepth)
        logger.info("Block size = %s", block_size)
        logger.info("Random size = %s", random_size)
        logger.info("Write pattern = %s", write_pattern)
        logger.info("Duration = %s", duration)
        logger.info("IO file = %s", self._io_file)
        logger.info("File size = %s GB", self._file_size)

        read_iops = read_bw = write_iops = write_bw = 0.0
        cpu_usage = {}

        try:
            if random_size:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                               f' -o{iodepth} -b{block_size} -r{random_size} '
                               f'-Sh -D -L -w{write_pattern} -d{duration} '
                               f'-c{self._file_size}G {self._io_file}')
            else:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                               f' -o{iodepth} -b{block_size} '
                               f'-w{write_pattern} -Sh -D -d{duration} -L '
                               f'-c{self._file_size}G {self._io_file}')

            str_output = self._api.io_command(str_command)

            if not str_output:
                raise RuntimeError("No output returned from io_command.")

            read_io_section = re.search(r'Read IO(.*?)Write IO', str_output,
                                        re.S)
            write_io_section = re.search(r'Write IO(.*?)(\n\n|\Z)', str_output,
                                         re.S)

            if read_io_section:
                read_io_text = read_io_section.group(1)
                read_pattern = re.compile(r'total:\s*([\d\s|.]+)')
                read_match = read_pattern.search(read_io_text)

                if read_match:
                    read_values = read_match.group(1).split('|')
                    read_iops = read_values[3].strip()
                    read_bw = read_values[2].strip()
                    logger.debug('read_iops = %s', read_iops)
                    logger.debug('read_bw = %s', read_bw)

            if write_io_section:
                write_io_text = write_io_section.group(1)
                write_pattern = re.compile(r'total:\s*([\d\s|.]+)')
                write_match = write_pattern.search(write_io_text)

                if write_match:
                    write_values = write_match.group(1).split('|')
                    write_iops = write_values[3].strip()
                    write_bw = write_values[2].strip()
                    logger.debug('write_iops = %s', write_iops)
                    logger.debug('write_bw = %s', write_bw)

            cpu_pattern = re.compile(
                r"\s+\d+\|\s+(\d+)\|\s+([\d\.]+)%\|\s+([\d\.]+)%\|\s+"
                r"([\d\.]+)%\|\s+([\d\.]+)%"
            )
            for match in cpu_pattern.finditer(str_output):
                cpu_id = int(match.group(1))
                logger.debug('cpu_id = %d', cpu_id)
                usage = {
                    "Total": float(match.group(2)),
                    "User": float(match.group(3)),
                    "Kernel": float(match.group(4)),
                    "Idle": float(match.group(5)),
                }
                cpu_usage[cpu_id] = usage
                logger.debug('Total = %.2f', cpu_usage[cpu_id]["Total"])
                logger.debug('User = %.2f', cpu_usage[cpu_id]["User"])
                logger.debug('Kernel = %.2f', cpu_usage[cpu_id]["Kernel"])
                logger.debug('Idle = %.2f', cpu_usage[cpu_id]["Idle"])

        except Exception as e:
            logger.error("Error occurred in run_io_operation: %s", e)
            raise

        return (
            float(read_bw or 0.0),
            float(read_iops or 0.0),
            float(write_bw or 0.0),
            float(write_iops or 0.0),
            cpu_usage
        )

    @staticmethod
    def log_io_metrics(read_bw, read_iops, write_bw, write_iops, prefix=""):
        """Logs the I/O metrics for read and write bandwidth and IOPS.

        Args:
            read_bw (float): Read bandwidth.
            read_iops (float): Read IOPS.
            write_bw (float): Write bandwidth.
            write_iops (float): Write IOPS.
            prefix (str, optional): Prefix for log message to distinguish
            random/sequential metrics.
        """
        logger.info('%sread_bw = %.2f MBps', prefix, read_bw)  # 保留兩位小數
        logger.info('%sread_iops = %d', prefix, read_iops)
        logger.info('%swrite_bw = %.2f MBps', prefix, write_bw)  # 保留兩位小數
        logger.info('%swrite_iops = %d', prefix, write_iops)

    def log_target_limit(self, upper_iops, lower_iops, upper_bw, lower_bw,
                         prefix=""):
        """Logs the upper and lower limits for IOPS and bandwidth for
        validation.

        Args:
            upper_iops (float): Upper limit of IOPS.
            lower_iops (float): Lower limit of IOPS.
            upper_bw (float): Upper limit of bandwidth.
            lower_bw (float): Lower limit of bandwidth.
            prefix (str, optional): Prefix for log message to distinguish
            read/write metrics.
        """
        logger.debug('upper_%siops = %s', prefix, upper_iops)
        logger.debug('lower_%siops = %s', prefix, lower_iops)
        logger.debug('upper_%sbw = %s', prefix, upper_bw)
        logger.debug('lower_%sbw = %s', prefix, lower_bw)

    def validate_metrics(self, read_bw, read_iops, write_bw, write_iops,
                         criteria):
        """Validates the I/O performance metrics against given criteria.

        Args:
            read_bw (float): Read bandwidth.
            read_iops (float): Read IOPS.
            write_bw (float): Write bandwidth.
            write_iops (float): Write IOPS.
            criteria (dict): A dictionary of performance criteria including
            percentile, minimum, and standard deviation for IOPS and bandwidth.

        Raises:
            AssertionError: If the metrics fall outside of the calculated
            limits.
        """
        if read_iops and read_bw:
            pct_read_iops = criteria['percentile_read_iops'][0]
            min_read_iops = criteria['min_read_iops']
            std_dev_read_iops = criteria['std_dev_read_iops']

            upper_limit_read_iops = (pct_read_iops + std_dev_read_iops *
                                     self.READ_R_CFL)
            lower_limit_read_iops = (pct_read_iops - std_dev_read_iops *
                                     self.READ_L_CFL)
            if lower_limit_read_iops < 0:
                lower_limit_read_iops = min_read_iops

            pct_read_bw = criteria['percentile_read_bw'][0]
            min_read_bw = criteria['min_read_bw']
            std_dev_read_bw = criteria['std_dev_read_bw']

            upper_limit_read_bw = \
                pct_read_bw + std_dev_read_bw * self.READ_R_CFL
            lower_limit_read_bw = \
                pct_read_bw - std_dev_read_bw * self.READ_L_CFL
            if lower_limit_read_bw < 0:
                lower_limit_read_bw = min_read_bw

            self.log_target_limit(
                upper_limit_read_iops,
                lower_limit_read_iops,
                upper_limit_read_bw,
                lower_limit_read_bw,
                'read_'
            )

            assert upper_limit_read_iops > read_iops > lower_limit_read_iops
            assert upper_limit_read_bw > read_bw > lower_limit_read_bw

        if write_iops and write_bw:
            pct_write_iops = criteria['percentile_write_iops'][0]
            min_write_iops = criteria['min_write_iops']
            std_dev_write_iops = criteria['std_dev_write_iops']

            upper_limit_write_iops = (pct_write_iops + std_dev_write_iops *
                                      self.WRITE_R_CFL)
            lower_limit_write_iops = (pct_write_iops - std_dev_write_iops *
                                      self.WRITE_L_CFL)
            if lower_limit_write_iops < 0:
                lower_limit_write_iops = min_write_iops

            pct_write_bw = criteria['percentile_write_bw'][0]
            min_write_bw = criteria['min_write_bw']
            std_dev_write_bw = criteria['std_dev_write_bw']

            upper_limit_write_bw = \
                pct_write_bw + std_dev_write_bw * self.WRITE_R_CFL
            lower_limit_write_bw = \
                pct_write_bw - std_dev_write_bw * self.WRITE_L_CFL
            if lower_limit_write_bw < 0:
                lower_limit_write_bw = min_write_bw

            self.log_target_limit(
                upper_limit_write_iops,
                lower_limit_write_iops,
                upper_limit_write_bw,
                lower_limit_write_bw,
                'write_'
            )

            assert upper_limit_write_iops > write_iops > lower_limit_write_iops
            assert upper_limit_write_bw > write_bw > lower_limit_write_bw


class LinuxPerf(BasePerf):
    '''docstring'''
    def run_io_operation(self,
                         iodepth: int,
                         block_size: str,
                         random_size: Optional[str],
                         write_pattern: str,
                         duration: int) -> Tuple[float, float, float, float]:
        pass


class BasePerfFactory(ABC):
    '''docstring'''
    def __init__(self, api: BaseInterface):
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def initiate(self, **kwargs) -> BasePerf:
        pass


class PerfFactory(BasePerfFactory):
    def initiate(self, **kwargs) -> BasePerf:
        if self.os_type == 'Windows':
            return WindowsPerf(**kwargs)
        elif self.os_type == 'Linux':
            return LinuxPerf(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
