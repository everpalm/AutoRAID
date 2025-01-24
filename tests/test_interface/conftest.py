# Content of tests/test_interface/conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

from event.logging import EventFactory
# from interface.application_interface import ApplicationInterface as api

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)


@pytest.fixture(scope="package")
def os_event(amd64_system, network_api):
    """Fixture for setting up Windows Event monitoring for system errors.

    Args:
        amd64_system: The system instance to monitor for Windows Event logs.

    Returns:
        WindowsEvent: An instance of WindowsEvent for error logging.
    """
    print('\n\033[32m================== Setup Event Logging =========\033[0m')
    event = EventFactory(network_api)
    return event.initiate(platform=amd64_system)


@pytest.fixture(scope="function", autouse=True)
def test_check_error(os_event):
    """Fixture to clear previous Windows event logs and check for specific
    errors after each test function.

    Yields:
        Clears event logs and checks for errors upon test completion.

    Raises:
        AssertionError: If specific errors (ID 51 or 157) are detected in logs
    """
    print('\n\033[32m================== Clear Event Log =============\033[0m')
    yield os_event.clear_error()
    print('\n\033[32m================== Check Event Log =============\033[0m')
    errors = []
    if os_event.find_error(
        "System",
        51,
        r'An error was detected on device (\\\w+\\\w+\.+)'
    ):
        errors.append("Error 51 detected in system logs.")

    if os_event.find_error("System", 157,
                           r'Disk (\d+) has been surprise removed.'):
        errors.append("Error 157 detected: Disk surprise removal.")

    if errors:
        raise AssertionError(f"Detected errors: {errors}")
