# Contents of test_win_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from amd_desktop.amd64_partition import WindowsVolume

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def win_partition(target_system):
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
    return WindowsVolume(platform=target_system)


# @pytest.fixture(scope="module")
# def test_startup(win_partition: WindowsVolume):
#     """Fixture to set up diskpart
#     Args:
#         target_system: The system instance to run diskpart.
#     Returns:
#         AMD64MultiPathStress: Instance for disk partitioning.
#     """
#     print('\n\033[32m================ Setup Diskpart ============\033[0m')
#     yield win_partition.startup()
#     print('\n\033[32m================ Teardown Diskpart =========\033[0m')
#     win_partition.close()


# @pytest.mark.order(1)
class TestWindowsVolume:
    # @pytest.fixture(scope="module")
    # def test_startup(self, win_partition: WindowsVolume):
    #     """Fixture to set up diskpart
    #     Args:
    #         target_system: The system instance to run diskpart.
    #     Returns:
    #         AMD64MultiPathStress: Instance for disk partitioning.
    #     """
    #     print('\n\033[32m================ Setup Diskpart ============\033[0m')
    #     yield win_partition.startup()
    #     print('\n\033[32m================ Teardown Diskpart =========\033[0m')
    #     win_partition.close()

    """
    Test suite for verifying Windows Warm Boot functionality.
    """
    def test_windows_execute(self, win_partition: WindowsVolume):
        """
        Execute a Windows Warm Boot and verify successful reset.

        This test executes a warm boot operation on the SUT (System Under
        Test) using the `win_warmboot` fixture. It then checks if the warm
        boot was successful and waits for a specified `RESET_DURATION`.

        Args:
            win_warmboot: The warm boot execution fixture.
        """
        result = win_partition.execute()
        logger.info('result = %s', result)

    # def test_1(self, win_partition: WindowsVolume):
    #     """
    #     Execute a Windows Warm Boot and verify successful reset.

    #     This test executes a warm boot operation on the SUT (System Under
    #     Test) using the `win_warmboot` fixture. It then checks if the warm
    #     boot was successful and waits for a specified `RESET_DURATION`.

    #     Args:
    #         win_warmboot: The warm boot execution fixture.
    #     """
    #     result = win_partition.execute1()
    #     logger.info('test1 = %s', result)

    # def test_2(self, win_partition: WindowsVolume):
    #     """
    #     Execute a Windows Warm Boot and verify successful reset.

    #     This test executes a warm boot operation on the SUT (System Under
    #     Test) using the `win_warmboot` fixture. It then checks if the warm
    #     boot was successful and waits for a specified `RESET_DURATION`.

    #     Args:
    #         win_warmboot: The warm boot execution fixture.
    #     """
    #     result = win_partition.execute2()
    #     logger.info('test2 = %s', result)
