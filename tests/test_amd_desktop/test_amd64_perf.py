# Contents of amd64_performance.py
'''Module for testing AMD64 system NVM performance. This module includes
   unit tests for Random, Sequential, and Ramp-up Read/Write performance,
   leveraging pytest fixtures and parameterized tests.

   Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest
# import os
# from amd_desktop.amd64_event import WindowsEvent as we

# Mark entire module
logger = logging.getLogger(__name__)
# logging.getLogger(__name__).setLevel(logging.DEBUG)

READ_R_CFL = 3
READ_L_CFL = 10
WRITE_R_CFL = 3
WRITE_L_CFL = 7


def log_target_limit(upper_iops, lower_iops, upper_bw, lower_bw, prefix=""):
    """Logs the upper and lower limits for IOPS and bandwidth for validation.

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
    logger.info('%sread_bw = %.2f', prefix, read_bw)  # 保留兩位小數
    logger.info('%sread_iops = %d', prefix, read_iops)
    logger.info('%swrite_bw = %.2f', prefix, write_bw)  # 保留兩位小數
    logger.info('%swrite_iops = %d', prefix, write_iops)


def validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria):
    """Validates the I/O performance metrics against given criteria.

    Args:
        read_bw (float): Read bandwidth.
        read_iops (float): Read IOPS.
        write_bw (float): Write bandwidth.
        write_iops (float): Write IOPS.
        criteria (dict): A dictionary of performance criteria including
        percentile, minimum, and standard deviation for IOPS and bandwidth.

    Raises:
        AssertionError: If the metrics fall outside of the calculated limits.
    """
    if read_iops and read_bw:
        pct_read_iops = criteria['percentile_read_iops'][0]
        min_read_iops = criteria['min_read_iops']
        std_dev_read_iops = criteria['std_dev_read_iops']

        upper_limit_read_iops = (pct_read_iops + std_dev_read_iops *
                                 READ_R_CFL)
        lower_limit_read_iops = (pct_read_iops - std_dev_read_iops *
                                 READ_L_CFL)
        if lower_limit_read_iops < 0:
            lower_limit_read_iops = min_read_iops

        pct_read_bw = criteria['percentile_read_bw'][0]
        min_read_bw = criteria['min_read_bw']
        std_dev_read_bw = criteria['std_dev_read_bw']

        upper_limit_read_bw = pct_read_bw + std_dev_read_bw * READ_R_CFL
        lower_limit_read_bw = pct_read_bw - std_dev_read_bw * READ_L_CFL
        if lower_limit_read_bw < 0:
            lower_limit_read_bw = min_read_bw

        log_target_limit(upper_limit_read_iops, lower_limit_read_iops,
                         upper_limit_read_bw, lower_limit_read_bw, 'read_')

        assert upper_limit_read_iops > read_iops > lower_limit_read_iops
        assert upper_limit_read_bw > read_bw > lower_limit_read_bw

    if write_iops and write_bw:
        pct_write_iops = criteria['percentile_write_iops'][0]
        min_write_iops = criteria['min_write_iops']
        std_dev_write_iops = criteria['std_dev_write_iops']

        upper_limit_write_iops = (pct_write_iops + std_dev_write_iops *
                                  WRITE_R_CFL)
        lower_limit_write_iops = (pct_write_iops - std_dev_write_iops *
                                  WRITE_L_CFL)
        if lower_limit_write_iops < 0:
            lower_limit_write_iops = min_write_iops

        pct_write_bw = criteria['percentile_write_bw'][0]
        min_write_bw = criteria['min_write_bw']
        std_dev_write_bw = criteria['std_dev_write_bw']

        upper_limit_write_bw = pct_write_bw + std_dev_write_bw * WRITE_R_CFL
        lower_limit_write_bw = pct_write_bw - std_dev_write_bw * WRITE_L_CFL
        if lower_limit_write_bw < 0:
            lower_limit_write_bw = min_write_bw

        log_target_limit(upper_limit_write_iops, lower_limit_write_iops,
                         upper_limit_write_bw, lower_limit_write_bw, 'write_')

        assert upper_limit_write_iops > write_iops > lower_limit_write_iops
        assert upper_limit_write_bw > write_bw > lower_limit_write_bw


@pytest.mark.PERFORMANCE
class TestRandomReadWrite:
    ''' Test AMD64 NVM Random Read Write Performance
        Performance of the AMD64 system
        Attributes:
            write_pattern: 0 - full read, 100 - full write
            io_depth: power of two. Min 1, max 32
            flaky: Max try 3 times, delay 60 secounds
    # '''
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('io_depth', [2**power for power in range(6)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, io_depth,
                              my_mdb):
        """Test random I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write io_depth (int): The I/O depth, ranging from 1 to 32.
            my_mdb (object): Database instance for aggregating metrics.
        """
        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(io_depth, '4k', '4k', write_pattern,
                                         15)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'random_')

        # criteria = my_mdb.aggregate_random_metrics(write_pattern, io_depth)
        # logger.debug('write_pattern = %s', write_pattern)
        # logger.debug('io_depth = %s', io_depth)
        # logger.debug('result = %s', criteria)  # 注意：這裡的變數名是 criteria

        # validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria)


@pytest.mark.PERFORMANCE
class TestSequentialReadWrite:
    ''' Test AMD64 NVM Sequential Read Write Performanceutdown -h
        Performance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in
            advance
    '''
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('block_size',
                             [f'{2**pwr}k' for pwr in range(2, 8)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, block_size,
                              my_mdb):
        """Test sequential I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write.
            block_size (str): Block size in kilobytes, ranging from 4k to 128k.
            my_mdb (object): Database instance for aggregating metrics.
        """
        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(32, block_size, None, write_pattern,
                                         156)
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'sequential_')

        # criteria = my_mdb.aggregate_sequential_metrics(write_pattern,
        #                                                block_size)
        # logger.debug('write_pattern = %s', write_pattern)
        # logger.debug('block_size = %s', block_size)
        # logger.debug('criteria = %s', criteria)

        # validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria)


@pytest.mark.PERFORMANCE
class TestRampTimeReadWrite:
    ''' Test AMD64 NVM Ramp-up Time Read Write
        Performance of the AMD64 system
        Fixtures:
            target_perf:
            ramp_times:
            write_pattern:
            my_mdb:
    '''
    @pytest.mark.skip(reason="Discerned")
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('ramp_times', list(range(120, 181, 10)))
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, ramp_times,
                              my_mdb):
        """Test ramp-up time I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write.
            ramp_times (int): Ramp-up time in seconds.
            my_mdb (object): Database instance for aggregating metrics.
        """
        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(1, '4k', '4k', write_pattern,
                                         ramp_times)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'ramp_')

        result = my_mdb.aggregate_ramp_metrics(write_pattern,
                                               ramp_times)
        logger.debug('write_pattern = %s', write_pattern)
        logger.debug('ramp_times = %s', ramp_times)
        logger.debug('result = %s', result)
