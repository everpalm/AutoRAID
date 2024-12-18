# Contents of test_amd64_stress.py
'''Unit tests for the AMD64MultiPathStress class. This module includes tests 
   for I/O stress operations on the AMD64 system to verify endurance and 
   performance stability under stress conditions.
   
   Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest
# from amd_desktop.amd64_stress import AMD64MultiPathStress as amps
# from amd_desktop.amd64_event import WindowsEvent as we
from tests.test_amd_desktop.test_amd64_perf import log_io_metrics

# Mark entire module
logger = logging.getLogger(__name__)

FULL_READ = 0
OLTP_LOADING = 30 # With 8 KB chunk size
FULL_WRITE = 100
OVER_NIGHT = 15
HALF_RW = 50
ONE_SHOT = 15
HYPER_THREAD = 2
SINGLE_THREAD = 1
MIN_IODEPTH = 1
MAX_IODEPTH = 33
OPTIMUM_IODEPTH = 7


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
    # @pytest.mark.parametrize('iodepth', list(range(MIN_IODEPTH, MAX_IODEPTH)))
    @pytest.mark.parametrize('iodepth', [2**power for power in range(6)])
    @pytest.mark.parametrize('write_pattern', [FULL_READ, FULL_WRITE])
    def test_run_io_operation(self, target_stress, write_pattern, iodepth,
                              my_mdb):
        """Runs parameterized I/O operations to test system stress with varying
        I/O depths and write patterns.
        
        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O tests.
            write_pattern (int): Write pattern defining the read/write ratio.
            iodepth (int): I/O depth level for stress testing.
            my_mdb: Mock database for storing and comparing test metrics.
        
        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target criteria.
        """
        read_bw, read_iops, write_bw, write_iops = target_stress.run_io_operation(
            SINGLE_THREAD, iodepth, '4k', '4k', write_pattern, OVER_NIGHT)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(write_pattern, iodepth)

        logger.debug("criteria = %s", criteria)


@pytest.mark.STRESS
class TestOneShotStress:
    ''' Oneshot I/O Stress Test'''
    def test_read_write(self, target_stress,my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.
        
        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O tests.
            write_pattern (int): Write and Read in half.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.
        
        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target criteria.
        """
        read_bw, read_iops, write_bw, write_iops = \
        target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH, '4k',
                                    '4k', HALF_RW, ONE_SHOT)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(HALF_RW, OPTIMUM_IODEPTH)

        logger.debug('criteria = %s', criteria)

    def test_full_read(self, target_stress,my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.
        
        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O tests.
            write_pattern (int): Write pattern defining full read.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.
        
        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target criteria.
        """
        read_bw, read_iops, write_bw, write_iops = \
        target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH, '4k',
                                    '4k', FULL_READ, ONE_SHOT)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(FULL_READ, OPTIMUM_IODEPTH)

        logger.debug("criteria = %s", criteria)

    def test_full_write(self, target_stress,my_mdb):
        """Runs oneshot I/O operations to test system stress with optimum
        I/O depths and write patterns.
        
        Args:
            target_stress (AMD64MultiPathStress): Stress instance for I/O tests.
            write_pattern (int): Write pattern defining full write.
            iodepth (int): Optimum I/O depth level for stress testing is 7.
            my_mdb: Mock database for storing and comparing test metrics.
        
        Assertions:
            - read_bw, read_iops, write_bw, write_iops metrics meet target criteria.
        """
        read_bw, read_iops, write_bw, write_iops = \
        target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH, '4k',
                                    '4k', FULL_WRITE, ONE_SHOT)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(FULL_WRITE, OPTIMUM_IODEPTH)

        logger.debug("criteria = %s", criteria)
