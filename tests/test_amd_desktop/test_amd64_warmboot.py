# Contents of test_amd64_coldboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import time
import pytest
from tests.test_amd_desktop.test_amd64_stress import TestOneShotStress
# from amd_desktop.amd64_warmboot import WindowsWarmBoot as wwb
from amd_desktop.amd64_warmboot import WarmBootFactory

logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
HALF_RW = 50
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7
RESET_DURATION = 30


@pytest.fixture(scope="module", autouse=True)
# def win_warmboot(target_system):
def win_warmboot(amd64_system, cmdopt):
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
    # return wwb(platform=target_system)
    warmboot = WarmBootFactory()
    return warmboot.initiate(os_type=cmdopt.get('os_type'),
                             platform=amd64_system)


@pytest.mark.order(1)
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
        assert result, "Windows Warm Boot execution failed."
        logger.info("Windows Warm Boot executed successfully.")

        time.sleep(RESET_DURATION)

    @pytest.mark.flaky(reruns=3, reruns_delay=10)
    def test_ping_after_warmboot(self, target_ping):
        """
        Verify network connectivity after a Windows Warm Boot.

        This test pings the target system after a warm boot to ensure network
        connectivity is restored. It uses the `target_ping` fixture and logs
        various ping statistics. The test is marked as flaky and will be rerun
        up to 3 times with a 10-second delay between reruns if it initially
        fails, to account for potential network instability after a reboot.

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

        # Check whether return value is True, which stands for the ping success
        assert result is True


@pytest.mark.order(2)
class TestWindowsWarmBootStress(TestOneShotStress):
    """Stress tests for Windows Warm Boot functionality. (Inherits from Toss)
    """
