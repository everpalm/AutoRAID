# Contents of amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import re
from amd_desktop.win10_interface import Win10Interface as win10
from typing import List

logger = logging.getLogger(__name__)

class AMD64MultiPathStress(object):
    def __init__(self, write_pattern, duration, io_paths: List):
        self.write_pattern = write_pattern
        self.duration = duration
        self.io_paths = io_paths
        self.api = win10()

    def run_io_operation(self, thread, iodepth, block_size, random_size,
            write_pattern, duration):

        logger.debug(f'thread = {thread}')
        logger.debug(f'iodepth = {iodepth}')
        logger.debug(f'block_size = {block_size}')
        logger.debug(f'random_size = {random_size}')
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'duration = {duration}')
        logger.debug(f'self._io_file = {self.io_paths}')
        
        read_iops = read_bw = write_iops = write_bw = None
        list_io_path = [f'{drive_letter}:\\IO.dat' for drive_letter, _ in self.io_paths]
        print(f'list_io_path = {list_io_path}')
        print(f'{" ".join(list_io_path)}')
        try:
            str_command = (f'diskspd -c1 -t{thread}'
            f' -o{iodepth} -b{block_size} -r{random_size}'
            f' -w{write_pattern} -d{duration} -Sh -D -c2G'
            f' {" ".join(list_io_path)}')
            
            str_output = self.api.io_command(str_command)
            
            if not str_output:
                raise RuntimeError("No output returned from io_command.")
        
            read_io_section = re.search(r'Read IO(.*?)Write IO', str_output,
                re.S)
            write_io_section = re.search(r'Write IO(.*?)(\n\n|\Z)',
                str_output, re.S)
            # logger.debug(f'write_io_section = {write_io_section.group(1)}')

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