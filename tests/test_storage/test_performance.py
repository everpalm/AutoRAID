# Contents of test_performance.py
'''
Module for testing AMD64/Intelx86 storage I/O performance. This module
includes unit tests for Random, Sequential, and Ramp-up Read/Write performance,
leveraging pytest fixtures and parameterized tests.

Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest

# Mark entire module
logger = logging.getLogger(__name__)


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
                              my_mdb, machine_learn):
        """Test random I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write io_depth (int): The I/O depth, ranging from 1 to 32.
            my_mdb (object): Database instance for aggregating metrics.
        """
        result = machine_learn.aggregate_best_ramp_time()
        best_ramp_time = result["percentile_best_ramp_time"][0]
        logger.debug('best_ramp_time = %s', best_ramp_time)

        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(io_depth, '4k', '4k', write_pattern,
                                         int(best_ramp_time))

        logger.info('random_read_bw = %.2f MBps', read_bw)
        logger.info('random_read_iops = %d', read_iops)
        logger.info('random_write_bw = %.2f MBps', write_bw)
        logger.info('random_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_random_metrics(write_pattern, io_depth)
        logger.info('write_pattern = %s', write_pattern)
        logger.info('io_depth = %s', io_depth)
        logger.info('result = %s', criteria)

        target_perf.validate_metrics(read_bw, read_iops, write_bw, write_iops,
                                     criteria)


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
                              my_mdb, machine_learn):
        """Test sequential I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write.
            block_size (str): Block size in kilobytes, ranging from 4k to 128k.
            my_mdb (object): Database instance for aggregating metrics.
        """
        result = machine_learn.aggregate_best_ramp_time()
        best_ramp_time = result["percentile_best_ramp_time"][0]
        logger.debug('best_ramp_time = %s', best_ramp_time)

        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(32, block_size, None, write_pattern,
                                         int(best_ramp_time))

        logger.info('sequential_read_bw = %.2f MBps', read_bw)
        logger.info('sequential_read_iops = %d', read_iops)
        logger.info('sequential_write_bw = %.2f MBps', write_bw)
        logger.info('sequential_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_sequential_metrics(write_pattern,
                                                       block_size)
        logger.info('write_pattern = %s', write_pattern)
        logger.info('block_size = %s', block_size)
        logger.info('criteria = %s', criteria)

        target_perf.validate_metrics(read_bw, read_iops, write_bw, write_iops,
                                     criteria)


@pytest.mark.TRAINING
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
    @pytest.mark.parametrize('ramp_times', list(range(150, 191, 10)))
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

        logger.info('ramp_read_bw = %.2f MBps', read_bw)
        logger.info('ramp_read_iops = %d', read_iops)
        logger.info('ramp_write_bw = %.2f MBps', write_bw)
        logger.info('ramp_write_iops = %d', write_iops)

        result = my_mdb.aggregate_ramp_metrics(write_pattern,
                                               ramp_times)
        logger.debug('write_pattern = %s', write_pattern)
        logger.debug('ramp_times = %s', ramp_times)
        logger.debug('result = %s', result)


@pytest.mark.TRAINING
@pytest.mark.PERFORMANCE
class TestRandomReadWriteSample:
    ''' Test AMD64 NVM Random Read Write Performance
        Performance of the AMD64 system
        Attributes:
            write_pattern: 0 - full read, 100 - full write
            io_depth: power of two. Min 1, max 32
            flaky: Max try 3 times, delay 60 secounds
    '''
    @pytest.mark.parametrize('io_depth', [2**power for power in range(6)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, io_depth,
                              my_mdb, machine_learn):
        """Test random I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write io_depth (int): The I/O depth, ranging from 1 to 32.
            my_mdb (object): Database instance for aggregating metrics.
        """
        result = machine_learn.aggregate_best_ramp_time()
        best_ramp_time = result["percentile_best_ramp_time"][0]
        logger.debug('best_ramp_time = %s', best_ramp_time)

        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(io_depth, '4k', '4k', write_pattern,
                                         int(best_ramp_time))

        logger.info('random_read_bw = %.2f MBps', read_bw)
        logger.info('random_read_iops = %d', read_iops)
        logger.info('random_write_bw = %.2f MBps', write_bw)
        logger.info('random_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_random_metrics(write_pattern, io_depth)
        logger.debug('write_pattern = %s', write_pattern)
        logger.debug('io_depth = %s', io_depth)
        logger.debug('result = %s', criteria)


@pytest.mark.TRAINING
@pytest.mark.PERFORMANCE
class TestSequentialReadWriteSample:
    ''' Test AMD64 NVM Sequential Read Write Performanceutdown -h
        Performance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in
            advance
    '''
    @pytest.mark.parametrize('block_size',
                             [f'{2**pwr}k' for pwr in range(2, 8)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, block_size,
                              my_mdb, machine_learn):
        """Test sequential I/O operation performance.

        Args:
            target_perf (object): The performance target instance.
            write_pattern (int): Write pattern, 0 for full read, 100 for full
            write.
            block_size (str): Block size in kilobytes, ranging from 4k to 128k.
            my_mdb (object): Database instance for aggregating metrics.
        """
        result = machine_learn.aggregate_best_ramp_time()
        best_ramp_time = result["percentile_best_ramp_time"][0]
        logger.debug('best_ramp_time = %s', best_ramp_time)

        read_bw, read_iops, write_bw, write_iops, _ = \
            target_perf.run_io_operation(32, block_size, None, write_pattern,
                                         int(best_ramp_time))

        logger.info('sequential_read_bw = %.2f MBps', read_bw)
        logger.info('sequential_read_iops = %d', read_iops)
        logger.info('sequential_write_bw = %.2f MBps', write_bw)
        logger.info('sequential_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_sequential_metrics(write_pattern,
                                                       block_size)
        logger.debug('write_pattern = %s', write_pattern)
        logger.debug('block_size = %s', block_size)
        logger.debug('criteria = %s', criteria)
