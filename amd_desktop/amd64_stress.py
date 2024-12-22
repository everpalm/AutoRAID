# Contents of amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class AMD64MultiPathStress:
    """
    Class to perform multi-path I/O stress testing on AMD64 systems.

    This class uses the `Win10Interface` to execute I/O operations and analyze
    the performance under stress conditions by running disk speed tests with
    various parameters.

    Attributes:
        write_pattern (str): The write pattern to be used in the stress test.
        duration (int): Duration of the stress test in seconds.
        io_paths (List[str]): List of I/O paths (drive letters) where the
        stress test will be executed.
        api (Win10Interface): An instance of the Win10Interface class used to
                              execute commands on the Windows 10 environment.
    """
    CPU_GROUP = None

    def __init__(self, platform):
        """
        Initializes the AMD64MultiPathStress class with test parameters.

        Args:
            write_pattern (str): The write pattern to be used in the stress
            test.
            duration (int): Duration of the stress test in seconds.
            io_paths (List[str]): List of I/O paths (drive letters) where the
                                  stress test will be executed.
        """
        if AMD64MultiPathStress.CPU_GROUP is None:
            AMD64MultiPathStress.CPU_GROUP = "0,0"  # Default CPU group 0, CPU0
        self._platform = platform
        self.io_paths = self._platform.disk_info
        self._api = platform.api
        self._file_size = self._platform.memory_size * 2

    @classmethod
    def set_cpu_group(cls, cpu_group):
        """
        Sets the CPU affinity.

        Args:
            cpu_group (str): The CPU group to set (e.g., '0,1,2,3').
        """
        cls.CPU_GROUP = cpu_group
        logger.info("Manually set CPU_GROUP: %s", cls.CPU_GROUP)

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
            write_pattern (str): Write pattern percentage (e.g., '100' for
            write only).

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
        logger.info('thread = %s', thread)
        logger.info('iodepth = %s', iodepth)
        logger.info('block_size = %s', block_size)
        logger.info('random_size = %s', random_size)
        logger.info('write_pattern = %s', write_pattern)
        logger.info('duration = %s', duration)
        logger.debug('self._io_file = %s', self.io_paths)
        logger.debug('self._file_size = %s', self._file_size)

        read_iops = read_bw = write_iops = write_bw = 0.0
        cpu_usage = {}

        list_io_path = [f'{drive_letter}:\\IO.dat' for drive_letter,
                        _ in self.io_paths]
        logger.info('_io_file = %s', " ".join(list_io_path))

        try:
            str_command = (
                f'diskspd -c1 -ag{self.CPU_GROUP} -t{thread} -L -Sh -D'
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

            cpu_pattern = re.compile(
                r"\s+\d+\|\s+(\d+)\|\s+"
                r"([\d\.]+)%\|\s+([\d\.]+)%\|\s+([\d\.]+)%\|\s+([\d\.]+)%"
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
            float(read_bw),
            float(read_iops),
            float(write_bw),
            float(write_iops),
            cpu_usage
        )
