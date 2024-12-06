# Contents of test_amd64_coldboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import time
import pytest
import RPi.GPIO as gpio

from tests.test_amd_desktop.test_amd64_stress import TestAMD64MultiPathStress
from tests.test_amd_desktop.test_amd64_perf import log_io_metrics
from amd_desktop.amd64_event import WindowsEvent as we
from amd_desktop.amd64_warmboot import WindowsWarmBoot as wwb
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps

logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7

@pytest.fixture(scope="session")
def win_event(target_system):
    """Fixture for setting up Windows Event monitoring for system errors.
    
    Args:
        target_system: The system instance to monitor for Windows Event logs.
    
    Returns:
        WindowsEvent: An instance of WindowsEvent for error logging.
    """
    print('\n\033[32m================== Setup Win Event =============\033[0m')
    return we(platform=target_system)

@pytest.fixture(scope="module", autouse=True)
def test_check_error(win_event):
    """Fixture to clear previous Windows event logs and check for specific errors
    after each test function.
    
    Yields:
        Clears event logs and checks for errors upon test completion.
    
    Raises:
        AssertionError: If specific errors (ID 51 or 157) are detected in logs.
    """

    yield win_event.clear_error()

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

@pytest.fixture(scope="module", autouse=True)
def win_warmboot(target_system):
    return wwb(platform=target_system)


@pytest.mark.order(1)
class TestWindowsWarmBoot:

    def test_execute(self, win_warmboot):
        """Run <Warm Boot> tests to ensure SUT reset correctly."""
        result = win_warmboot.execute()
        assert result, "Windows Warm Boot execution failed. Check logs for details."
        logger.info("Windows Warm Boot executed successfully.")
        
        time.sleep(15)

    @pytest.mark.flaky(reruns=3, reruns_delay=10)
    def test_power_on(self, target_ping):
        result = target_ping.ping()
        logger.info(f'target_ping.sent = {target_ping.sent}')
        logger.info(f'target_ping.received = {target_ping.received}')
        logger.info(f'target_ping.lost = {target_ping.lost}')
        logger.info(f'target_ping.minimum = {target_ping.minimum}')
        logger.info(f'target_ping.maximum = {target_ping.maximum}')
        logger.info(f'target_ping.average = {target_ping.average}')
        logger.info(f'ping_instance.deviation = {target_ping.deviation}')

        # 检查返回值是否为True，表示ping成功
        assert result is True

@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(2)
@pytest.mark.parametrize('write_pattern', [FULL_READ, FULL_WRITE])
# class TestWindowsRunTimeIO(TestAMD64MultiPathStress):
class TestWindowsRunTimeIO:
    def test_run_io_operation(self, target_stress, write_pattern, my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_stress.run_io_operation(
            SINGLE_THREAD, OPTIMUM_IODEPTH, '4k', '4k', FULL_READ, ONE_SHOT)
    
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(write_pattern, OPTIMUM_IODEPTH)

        logger.debug('criteria = %s', criteria)