# Contents of tests/test_boot/test_amd64_reboot.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import time
import pytest
from tests.test_network.test_amd64_ping import TestAMD64Ping as Ping
from tests.test_storage.test_stress import TestOneShotStress as Stress
from boot.amd64_reboot import RebootFactory

logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
HALF_RW = 50
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7
RESET_DURATION = 30


@pytest.fixture(scope="module", autouse=True)
def win_boot(amd64, network_api):
    """
    Fixture to automatically execute a Windows Warm Boot for the test module.

    This fixture creates and returns a `wwb` object (presumably for warm boot
    execution) initialized with the provided `amd_system`.  It has a
    "module" scope, meaning it will be executed only once per test module,
    before any test functions are run.  The `autouse=True`
    parameter ensures that this fixture is automatically used by all test
    functions within the module, without needing to explicitly include it as a
    parameter.

    Args:
        amd_system: The target system object for warm boot execution.

    Returns:
        wwb: The warm boot execution object.
    """
    reboot = RebootFactory(network_api)
    print("\n\033[32m================== Setup Reboot Test ===========\033[0m")
    return reboot.initiate(platform=amd64)


class TestWindowsWarmBoot:
    """
    Test suite for verifying Windows Warm Boot functionality.
    """
    def test_warm_reset(self, win_boot):
        """
        Execute a Windows Warm Boot and verify successful reset.

        This test executes a warm boot operation on the SUT (System Under
        Test) using the `win_warmboot` fixture. It then checks if the warm
        boot was successful and waits for a specified `RESET_DURATION`.

        Args:
            win_warmboot: The warm boot execution fixture.
        """
        result = win_boot.warm_reset()
        assert result, "Windows Warm Boot execution failed."
        logger.info("Windows Warm Boot executed successfully.")

        time.sleep(RESET_DURATION)


class TestWindowsWarmBootPing(Ping):
    """
    Test suite for verifying Windows Warm Boot functionality with network
    """


class TestWindowsWarmBootStress(Stress):
    """
    Stress tests for Windows Warm Boot functionality. (Inherits from Toss)
    """
