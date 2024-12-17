# Contents of test_amd64_coldboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import time
import pytest
from tests.test_amd_desktop.test_amd64_stress import TestOneShotStress as Toss
from amd_desktop.amd64_warmboot import WindowsWarmBoot as wwb


logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
HALF_RW = 50
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7
RESET_DURATION = 30

# @pytest.fixture(scope="module")
# def win_event(target_system):
#     """Fixture for setting up Windows Event monitoring for system errors.

#     Args:
#         target_system: The system instance to monitor for Windows Event logs.

#     Returns:
#         WindowsEvent: An instance of WindowsEvent for error logging.
#     """
#     print('\n\033[32m================== Setup Win Event =============\033[0m')
#     return We(platform=target_system)

# @pytest.fixture(scope="module", autouse=True)
# def test_check_error(win_event):
#     """Fixture to clear previous Windows event logs and check for specific errors
#     after each test function.

#     Yields:
#         Clears event logs and checks for errors upon test completion.

#     Raises:
#         AssertionError: If specific errors (ID 51 or 157) are detected in logs.
#     """

#     yield win_event.clear_error()

#     errors = []
#     if win_event.find_error("System", 51, r'An error was detected on device (\\\w+\\\w+\.+)'):
#         # raise AssertionError("Error 51 detected in system logs.")
#         errors.append("Error 51 detected in system logs.")

#     if win_event.find_error("System", 157, r'Disk (\d+) has been surprise removed.'):
#         # raise AssertionError("Error 157 detected in system logs.")
#         errors.append("Error 157 detected: Disk surprise removal.")

#     if errors:
#         logger.error(f"Windows event errors detected: {errors}")
#         raise AssertionError(f"Detected errors: {errors}")

#     print('\n\033[32m================== Teardown Win Event ==========\033[0m')

@pytest.fixture(scope="module", autouse=True)
def win_warmboot(target_system):
    """
    Fixture to automatically execute a Windows Warm Boot for the test module.

    This fixture creates and returns a `wwb` object (presumably for warm boot
    execution) initialized with the provided `target_system`.  It has a
    "module" scope, meaning it will be executed only once per test module,
    before any test functions are run.  The `autouse=True` 
    parameter ensures that this fixture is automatically used by all test
    functions within the module, without needing to explicitly include it as a
    parameter.

    Args:
        target_system: The target system object for warm boot execution.

    Returns:
        wwb: The warm boot execution object.
    """
    return wwb(platform=target_system)


# @pytest.mark.order(1)
class TestWindowsWarmBoot:
    """
    Test suite for verifying Windows Warm Boot functionality.
    """
    def test_warmboot_execute(self, win_warmboot):
        """
        Execute a Windows Warm Boot and verify successful reset.

        This test executes a warm boot operation on the SUT (System Under
        Test) using the `win_warmboot` fixture. It then checks if the warm
        boot was successful and waits for a specified `RESET_DURATION`.

        Args:
            win_warmboot: The warm boot execution fixture.
        """
        result = win_warmboot.execute()
        assert result, "Windows Warm Boot execution failed. Check logs for details."
        logger.info("Windows Warm Boot executed successfully.")

        time.sleep(RESET_DURATION)

    @pytest.mark.flaky(reruns=3, reruns_delay=10)
    def test_ping_after_warmboot(self, target_ping):
        """
        Verify network connectivity after a Windows Warm Boot.

        This test pings the target system after a warm boot to ensure network 
        connectivity is restored. It uses the `target_ping` fixture and logs 
        various ping statistics. The test is marked as flaky and will be rerun 
        up to 3 times with a 10-second delay between reruns if it initially fails, 
        to account for potential network instability after a reboot.

        Args:
            target_ping: The ping fixture for the target system.
        """
        result = target_ping.ping()
        logger.info('target_ping.sent = %s', target_ping.sent)
        logger.info('target_ping.received = %s', target_ping.received)
        logger.info('target_ping.lost = %s', target_ping.lost)
        logger.info('target_ping.minimum = %s', target_ping.minimum)
        logger.info('target_ping.maximum = %s', target_ping.maximum)
        logger.info('target_ping.average = %s', target_ping.average)
        logger.info('ping_instance.deviation = %s', target_ping.deviation)

        # 检查返回值是否为True，表示ping成功
        assert result is True

    # def test_io_oneshot(self, target_stress,my_mdb):
    #     """Runs oneshot I/O operations to test system stress with optimum
    #     I/O depths and write patterns.

    #     Args:
    #         target_stress (AMD64MultiPathStress): Stress instance for I/O tests.
    #         write_pattern (int): Write pattern defining full read.
    #         iodepth (int): Optimum I/O depth level for stress testing is 7.
    #         my_mdb: Mock database for storing and comparing test metrics.

    #     Assertions:
    #         - read_bw, read_iops, write_bw, write_iops metrics meet target criteria.
    #     """
    #     read_bw, read_iops, write_bw, write_iops = \
    #     target_stress.run_io_operation(SINGLE_THREAD, OPTIMUM_IODEPTH, '4k',
    #                                    '4k', HALF_RW, ONE_SHOT)

    #     log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

    #     criteria = my_mdb.aggregate_stress_metrics(HALF_RW, OPTIMUM_IODEPTH)

    #     logger.debug(f'criteria = {criteria}')

# @pytest.mark.order(2)
class TestWindowsWarmBootStress(Toss):
    """Stress tests for Windows Warm Boot functionality. (Inherits from Toss)"""

