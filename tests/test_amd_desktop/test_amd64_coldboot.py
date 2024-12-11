'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
import RPi.GPIO as gpio

from tests.test_amd_desktop.test_amd64_stress import TestOneShotStress as Toss
from tests.test_raspberry.test_pi3_gpio import TestPowerOnSUT, TestPowerOffSUT
from unit.gpio import OperateGPIO as Og
# from amd_desktop.amd64_event import WindowsEvent as We

logger = logging.getLogger(__name__)

FULL_READ = 0
FULL_WRITE = 100
ONE_SHOT = 15
SINGLE_THREAD = 1
OPTIMUM_IODEPTH = 7


# @pytest.fixture(scope="session")
# def win_event(target_system):
#     """
#     Fixture for setting up Windows Event monitoring for system errors.

#     Args:
#         target_system: The system instance to monitor for Windows Event logs.

#     Returns:
#         WindowsEvent: An instance of WindowsEvent for error logging.
#     """
#     print('\n\033[32m================== Setup Win Event =============\033[0m')
#     return We(platform=target_system)


@pytest.fixture(scope="module", autouse=True)
def test_check_error(win_event):
    """
    Fixture to clear previous Windows event logs and check for specific errors
    after each test function.

    Yields:
        Clears event logs and checks for errors upon test completion.

    Raises:
        AssertionError: If specific errors (ID 51 or 157) are detected in logs.
    """
    yield win_event.clear_error()

    errors = []
    if win_event.find_error("System", 51,
                            r'An error was detected on device (\\\w+\\\w+\.+)'):
        errors.append("Error 51 detected in system logs.")

    if win_event.find_error("System", 157,
                            r'Disk (\d+) has been surprise removed.'):
        errors.append("Error 157 detected: Disk surprise removal.")

    if errors:
        logger.error("Windows event errors detected: %s", errors)
        raise AssertionError(f"Detected errors: {errors}")

    print('\n\033[32m================== Teardown Win Event ==========\033[0m')


@pytest.fixture(scope="module")
def rpi_gpio(my_pins):
    """
    Fixture for setting up the GPIO interface on Raspberry Pi.

    Args:
        my_pins: The pin configuration for the GPIO.

    Yields:
        OperateGPIO: An instance of OperateGPIO for managing the GPIO pins.
    """
    print('\n================== Setup Relay ================================')
    amd_mgi = Og(my_pins, gpio.BOARD)

    yield amd_mgi
    print('\n================== Teardown Relay =============================')

    # Clear GPIO
    amd_mgi.clear_gpio()


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(1)
class TestRelayOff(TestPowerOffSUT):
    """Test case for turning the relay off."""


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(2)
class TestRelayOn(TestPowerOnSUT):
    """Test case for turning the relay on."""


@pytest.mark.skip(reason="Compatibility issue")
@pytest.mark.order(3)
class TestWindowsColdBootStress(Toss):
    """Test case for Windows cold boot stress."""