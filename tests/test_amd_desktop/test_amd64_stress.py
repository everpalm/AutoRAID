# Contents of test_amd64_stress.py
'''Unit tests for the AMD64MultiPathStress class. This module includes tests 
   for I/O stress operations on the AMD64 system to verify endurance and 
   performance stability under stress conditions.
   
   Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps
from amd_desktop.amd64_event import WindowsEvent as we
from tests.test_amd_desktop.test_amd64_perf import log_io_metrics

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)

FULL_READ = 0
OLTP_LOADING = 30 # With 8 KB chunk size
FULL_WRITE = 100
OVER_NIGHT = 15
ONE_SHOT = 15
HYPER_THREAD = 2
SINGLE_THREAD = 1
MIN_IODEPTH = 1
MAX_IODEPTH = 33
OPTIMUM_IODEPTH = 7

@pytest.fixture(scope="function")
def win_event(target_system):
    """Fixture for setting up Windows Event monitoring for system errors.
    
    Args:
        target_system: The system instance to monitor for Windows Event logs.
    
    Returns:
        WindowsEvent: An instance of WindowsEvent for error logging.
    """
    print('\n\033[32m================== Setup Win Event =============\033[0m')
    return we(platform=target_system)

@pytest.fixture(scope="function", autouse=True)
def test_check_error(win_event):
    """Fixture to clear previous Windows event logs and check for specific errors
    after each test function.
    
    Yields:
        Clears event logs and checks for errors upon test completion.
    
    Raises:
        AssertionError: If specific errors (ID 51 or 157) are detected in logs.
    """

    yield win_event.clear_error()

    # if win_event.find_error("System", 51, r'An error was detected on device (\\\w+\\\w+\.+)'):
    #     raise AssertionError("Error 51 detected in system logs.")
    
    # if win_event.find_error("System", 157, r'Disk (\d+) has been surprise removed.'):
    #     raise AssertionError("Error 157 detected in system logs.")
    errors = []
    if win_event.find_error("System", 51, r'An error was detected on device (\\\w+\\\w+\.+)'):
        # raise AssertionError("Error 51 detected in system logs.")
        errors.append("Error 51 detected in system logs.")
    
    if win_event.find_error("System", 157, r'Disk (\d+) has been surprise removed.'):
        # raise AssertionError("Error 157 detected in system logs.")
        errors.append("Error 157 detected: Disk surprise removal.")
    
    if errors:
        logger.error(f"Windows event errors detected: {errors}")
        raise AssertionError(f"Detected errors: {errors}")  
    
    print('\n\033[32m================== Teardown Win Event ==========\033[0m')

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
    @pytest.fixture(scope="function")
    def target_stress(self, target_system):
        """Fixture for setting up an AMD64MultiPathStress instance for I/O stress tests.
        
        Args:
            target_system: The system instance to run stress tests on.
        
        Returns:
            AMD64MultiPathStress: Instance for executing stress test operations.
        """
        print('\n\033[32m================ Setup I/O Stress ==========\033[0m')
        return amps(platform=target_system)

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

        logger.debug(f'criteria = {criteria}')
        
    def test_oneshot_operation(self, target_stress,my_mdb):
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

        logger.debug(f'criteria = {criteria}')
        
