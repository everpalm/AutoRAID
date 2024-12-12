'''Copyright (c) 2024 Jaron Cheng'''
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class AMD64Perf:
    '''AMD64 Performance
    Args:
        platform: 平台對象
        io_file: IO操作的文件路徑
    '''
    def __init__(self, platform, io_file):
        self._io_file = io_file
        self._platform = platform
        self._api = platform.api
        self._cpu_num = self._platform.cpu_num
        self._thread = self._cpu_num * 2
        self._file_size = self._platform.memory_size * 2

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
        # 使用 lazy % formatting
        logger.info("Thread count = %s", self._thread)
        logger.info("IO depth = %s", iodepth)
        logger.info("Block size = %s", block_size)
        logger.info("Random size = %s", random_size)
        logger.info("Write pattern = %s", write_pattern)
        logger.info("Duration = %s", duration)
        logger.info("IO file = %s", self._io_file)
        logger.info("File size = %s", self._file_size)

        read_iops = read_bw = write_iops = write_bw = None

        try:
            # 構建命令，根據是否有隨機大小參數
            if random_size:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                               f' -o{iodepth} -b{block_size} -r{random_size} -Sh -D -L '
                               f' -w{write_pattern} -d{duration} -c{self._file_size}G'
                               f' {self._io_file}')
            else:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                               f' -o{iodepth} -b{block_size} -w{write_pattern} -Sh -D '
                               f' -d{duration} -L -c{self._file_size}G {self._io_file}')

            # 執行命令
            str_output = self._api.io_command(str_command)

            if not str_output:
                raise RuntimeError("No output returned from io_command.")

            # 使用正則表達式提取讀寫IO信息
            read_io_section = re.search(r'Read IO(.*?)Write IO', str_output, re.S)
            write_io_section = re.search(r'Write IO(.*?)(\n\n|\Z)', str_output, re.S)

            # 解析讀取IO信息
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

            # 解析寫入IO信息
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

        except Exception as e:
            logger.error("Error occurred in run_io_operation: %s", e)
            raise
        # 確保返回值為浮點數，如果解析失敗則返回0.0
        return (
            float(read_bw or 0.0),
            float(read_iops or 0.0),
            float(write_bw or 0.0),
            float(write_iops or 0.0)
        )