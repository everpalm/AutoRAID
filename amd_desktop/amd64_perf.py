# Contents of amd64_perf.py
'''Copyright (c) 2024 Jaron Cheng'''
import re
import logging
# from amd_desktop.win10_interface import Win10Interface as win10
# from typing import Dict

logger = logging.getLogger(__name__)

class AMD64Perf:

    def __init__(self, platform, io_file):
        self._io_file = io_file
        self._platform = platform
        self._api = platform.api
        self._cpu_num = self._platform.cpu_num
        self._thread = self._cpu_num * 2
        self._file_size = self._platform.memory_size * 2
                
    def run_io_operation(self, iodepth, block_size, random_size,
            write_pattern, duration):
        ''' Run DISKSPD
            Args:
                thread 2 -t2
                iodepth 32 -o32
                blocksize 4k -b4k
                random 4k -r4k
                write 0% -w0
                duration 120 seconds -d120
                writethrough -Sh
                data ms -D
                5GB test file -c5g
                cpu 12 -c12
                affinity 3 -a3 (running on cpu 3)
            Returns: read bw, read iops, write bw, write iops
            Raises: Any errors occurs while invoking diskspd
        '''
        logger.info(f'self._thread = {self._thread}')
        logger.info(f'iodepth = {iodepth}')
        logger.info(f'block_size = {block_size}')
        logger.info(f'random_size = {random_size}')
        logger.info(f'write_pattern = {write_pattern}')
        logger.info(f'duration = {duration}')
        logger.info(f'self._io_file = {self._io_file}')
        logger.info(f'self._file_size = {self._file_size}')
        
        read_iops = read_bw = write_iops = write_bw = None
        try:
            if random_size:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                f' -o{iodepth} -b{block_size} -r{random_size} -Sh -D -L '
                f' -w{write_pattern} -d{duration} -c{self._file_size}G'
                f' {self._io_file}')
            else:
                str_command = (f'diskspd -c{self._cpu_num} -t{self._thread}'
                    f' -o{iodepth} -b{block_size} -w{write_pattern} -Sh -D '
                    f' -d{duration} -L -c{self._file_size}G {self._io_file}')
            
            str_output = self._api.io_command(str_command)
            
            if not str_output:
                raise RuntimeError("No output returned from io_command.")
        
            read_io_section = re.search(r'Read IO(.*?)Write IO', str_output,
                re.S)
            write_io_section = re.search(r'Write IO(.*?)(\n\n|\Z)',
                str_output, re.S)

            if read_io_section:
                read_io_text = read_io_section.group(1)

                # Extract total and I/O per s values
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

                # Extract total and I/O per s value
                write_pattern = re.compile(r'total:\s*([\d\s|.]+)')
                write_match = write_pattern.search(write_io_text)
                if write_match:
                    write_values = write_match.group(1).split('|')
                    write_iops = write_values[3].strip()
                    write_bw = write_values[2].strip()
                    logger.debug('write_iops = %s', write_iops)
                    logger.debug('write_bw = %s', write_bw)

        except Exception as e:
            logger.error(f"Error occurred in run_io_operation: {e}")
            raise
        finally:
            return float(read_bw), float(read_iops), float(write_bw), float(write_iops)
