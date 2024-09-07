# Contents of amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import re
# from amd_desktop.win10_interface import Win10Interface as win10
# from typing import List

logger = logging.getLogger(__name__)

class AMD64MultiPathStress(object):
    """
    Class to perform multi-path I/O stress testing on AMD64 systems.

    This class uses the `Win10Interface` to execute I/O operations and analyze
    the performance under stress conditions by running disk speed tests with
    various parameters.

    Attributes:
        write_pattern (str): The write pattern to be used in the stress test.
        duration (int): Duration of the stress test in seconds.
        io_paths (List[str]): List of I/O paths (drive letters) where the stress
                              test will be executed.
        api (Win10Interface): An instance of the Win10Interface class used to
                              execute commands on the Windows 10 environment.
    """
    def __init__(self, platform):
        """
        Initializes the AMD64MultiPathStress class with test parameters.

        Args:
            write_pattern (str): The write pattern to be used in the stress test.
            duration (int): Duration of the stress test in seconds.
            io_paths (List[str]): List of I/O paths (drive letters) where the
                                  stress test will be executed.
        """
        self._platform = platform
        self.io_paths = self._platform.disk_info
        # self.api = win10()
        self._api = platform.api
        self._file_size = self._platform.memory_size * 2

    def run_io_operation(self, thread, iodepth, block_size, random_size,
            write_pattern, duration):
        """
        Runs an I/O operation using the specified parameters and returns the 
        IOPS and bandwidth for both read and write operations.

        Args:
            thread (int): Number of threads to use in the I/O operation.
            iodepth (int): I/O depth (queue depth) for the operation.
            block_size (str): Block size for the I/O operation (e.g., '4K').
            random_size (str): Random size for the I/O operation.
            write_pattern (str): Write pattern percentage (e.g., '100' for write only).
            duration (int): Duration of the test in seconds.

        Returns:
            tuple: A tuple containing four float values:
                   (read_bw, read_iops, write_bw, write_iops)
                   where:
                   - read_bw (float): Read bandwidth.
                   - read_iops (float): Read IOPS.
                   - write_bw (float): Write bandwidth.
                   - write_iops (float): Write IOPS.

        Raises:
            RuntimeError: If no output is returned from the I/O command.
            Exception: If any other error occurs during the I/O operation,
                       it is logged and then re-raised to be handled by the
                       caller.
        """
        logger.info(f'thread = {thread}')
        logger.info(f'iodepth = {iodepth}')
        logger.info(f'block_size = {block_size}')
        logger.info(f'random_size = {random_size}')
        logger.info(f'write_pattern = {write_pattern}')
        logger.info(f'duration = {duration}')
        logger.debug(f'self._io_file = {self.io_paths}')
        logger.debug(f'self._file_size = {self._file_size}')

        read_iops = read_bw = write_iops = write_bw = None
        list_io_path = [f'{drive_letter}:\\IO.dat' for drive_letter,
                        _ in self.io_paths]
        logger.info(f'_io_file = {" ".join(list_io_path)}')

        try:
            str_command = (f'diskspd -c1 -t{thread} -L -Sh -D'
            f' -o{iodepth} -b{block_size} -r{random_size}'
            f' -w{write_pattern} -d{duration} -c{self._file_size}G'
            f' {" ".join(list_io_path)}')
            
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
            return (float(read_bw), float(read_iops), float(write_bw),
                    float(write_iops))