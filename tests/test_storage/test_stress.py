# Contents of test_storage.test_stress.py
'''Unit tests for the AMD64MultiPathStress class. This module includes tests
   for I/O stress operations on the AMD64 system to verify endurance and
   performance stability under stress conditions.

   Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest

# Mark entire module
logger = logging.getLogger(__name__)

# Write pattern
FULL_READ = 0
OLTP_WORKLOAD = 30  # With 8 KB chunk size
HALF_RW = 50
FULL_WRITE = 100

# Period
OVER_NIGHT = 15
ONE_SHOT = 15

# Threading
SINGLE_THREAD = 1
HYPER_THREAD = 2

# Outstanding I/O
OPTIMUM_IODEPTH = 7
MIN_IODEPTH = 1
MAX_IODEPTH = 33


@pytest.mark.dependency(name="general stress")
@pytest.mark.STRESS
class TestAMD64MultiPathStress:
    ''' Test I/O Stress
        Endurance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in
            advance
    '''
    @pytest.mark.parametrize('iodepth', [2**power for power in range(6)])
    @pytest.mark.parametrize('write_pattern', [FULL_READ, FULL_WRITE])
    def test_run_io_operation(self, target_stress, write_pattern, iodepth,
                              my_mdb):
        """Runs parameterized I/O operations to test system stress with varying
        I/O depths and write patterns.

        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O
            tests.
            write_pattern (int): Write pattern defining the read/write ratio.
            iodepth (int): I/O depth level for stress testing.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, iodepth, '4k', '4k',
                                           write_pattern, OVER_NIGHT)

        logger.info('stress_read_bw = %.2f MBps', read_bw)
        logger.info('stress_read_iops = %d', read_iops)
        logger.info('stress_write_bw = %.2f MBps', write_bw)
        logger.info('stress_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_stress_metrics(write_pattern, iodepth)

        logger.debug("criteria = %s", criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])


@pytest.mark.STRESS
class TestOneShotStress:
    ''' Oneshot I/O Stress Test'''
    def test_read_write(self, target_stress, my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.

        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O
            tests.
            write_pattern (int): Write and Read in half.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH,
                                           '4k', '4k', HALF_RW, ONE_SHOT)

        logger.info('stress_read_bw = %.2f MBps', read_bw)
        logger.info('stress_read_iops = %d', read_iops)
        logger.info('stress_write_bw = %.2f MBps', write_bw)
        logger.info('stress_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_stress_metrics(HALF_RW, OPTIMUM_IODEPTH)

        logger.debug('criteria = %s', criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])

    def test_full_read(self, target_stress, my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.

        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O
            tests.
            write_pattern (int): Write pattern defining full read.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH,
                                           '4k', '4k', FULL_READ, ONE_SHOT)

        logger.info('stress_read_bw = %.2f MBps', read_bw)
        logger.info('stress_read_iops = %d', read_iops)
        logger.info('stress_write_bw = %.2f MBps', write_bw)
        logger.info('stress_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_stress_metrics(FULL_READ, OPTIMUM_IODEPTH)

        logger.debug("criteria = %s", criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])

    def test_full_write(self, target_stress, my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.

        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O
            tests.
            write_pattern (int): Write pattern defining full write.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH,
                                           '4k', '4k', FULL_WRITE, ONE_SHOT)

        logger.info('stress_read_bw = %.2f MBps', read_bw)
        logger.info('stress_read_iops = %d', read_iops)
        logger.info('stress_write_bw = %.2f MBps', write_bw)
        logger.info('stress_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_stress_metrics(FULL_WRITE, OPTIMUM_IODEPTH)

        logger.debug("criteria = %s", criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])


@pytest.mark.STRESS
class TestOLTP:
    ''' Online Transaction Processing workload
        Fixture:
            target_stress
            my_mdb
        Parametrize:
            write_pattern 70% Read, 30% Write
            iodepth
    '''
    @pytest.mark.parametrize('iodepth', [2**power for power in range(6)])
    def test_run_io_operation(self, target_stress, iodepth, my_mdb):
        """Runs parameterized I/O operations to test system stress with varying
        I/O depths and write patterns.

        Args:
            target_stress (OLTP): Stress instance for I/O
            tests.
            write_pattern (int): Write pattern defining the read/write ratio.
            iodepth (int): I/O depth level for stress testing.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, iodepth, '8k', '8k',
                                           OLTP_WORKLOAD, OVER_NIGHT)

        logger.info('oltp_read_bw = %.2f MBps', read_bw)
        logger.info('oltp_read_iops = %d', read_iops)
        logger.info('oltp_write_bw = %.2f MBps', write_bw)
        logger.info('oltp_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_oltp_metrics(iodepth)

        logger.debug("criteria = %s", criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])


@pytest.mark.STRESS
class TestOLAP:
    ''' Online Analytical Processing workload
        Fixture:
            target_stress
            my_mdb
        Parametrize:
            512 KB block size
            1 thread per file
    '''
    @pytest.mark.parametrize('write_pattern', list(range(0, 101, 20)))
    def test_run_io_operation(self, target_stress, write_pattern, my_mdb):
        """Runs parameterized I/O operations to test system stress with varying
        I/O depths and write patterns.

        Args:
            target_stress (OLAP): Stress instance for I/O
            tests.
            write_pattern (int): Write pattern defining the read/write ratio.
            iodepth (int): I/O depth level for stress testing.
            my_mdb: Mock database for storing and comparing test metrics.

        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target
            criteria.
        """
        read_bw, read_iops, write_bw, write_iops, cpu_usage = \
            target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH,
                                           '512k', '512k', write_pattern,
                                           OVER_NIGHT)

        logger.info('olap_read_bw = %.2f MBps', read_bw)
        logger.info('olap_read_iops = %d', read_iops)
        logger.info('olap_write_bw = %.2f MBps', write_bw)
        logger.info('olap_write_iops = %d', write_iops)

        criteria = my_mdb.aggregate_olap_metrics(write_pattern)

        logger.debug("criteria = %s", criteria)
        logger.info("cpu_usage = %.2f%%", cpu_usage[0]["Total"])
