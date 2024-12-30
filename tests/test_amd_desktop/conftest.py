# Content of test_amd_desktop.conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

from amd_desktop.amd64_event import WindowsEvent as We
from amd_desktop.amd64_os import AMD64Windows
from amd_desktop.amd64_nvme import AMD64NVMe as amd64
from amd_desktop.amd64_perf import AMD64Perf as amd64perf
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps
from unit.amd64_interface import InterfaceFactory
from unit.application_interface import ApplicationInterface as api
from unit.mongodb import MongoDB as mdb
from unit.system_under_testing import RaspberryPi as rpi

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)


@pytest.fixture(scope="session")
def my_app(cmdopt):
    '''This is a docstring'''
    print('\n\033[32m================== Setup API ===================\033[0m')
    return api.create_interface(
        os_type=cmdopt.get('os_type'),
        mode=cmdopt.get('mode'),
        if_name=cmdopt.get('if_name'),
        config_file=cmdopt.get('config_file')
    )


@pytest.fixture(scope="session")
def windows_api(cmdopt):
    '''docstring'''
    print('\n\033[32m================== Setup Interface =============\033[0m')
    factory = InterfaceFactory()
    return factory.create_interface(
        os_type='Windows',
        mode='remote',
        if_name='wlan0',
        ssh_port='22',
        config_file=cmdopt.get('config_file')
    )


@pytest.fixture(scope="session")
def my_mdb():
    """
    Fixture to establish a connection to a MongoDB database.

    Establishes a connection to MongoDB with the specified parameters. This
    fixture has a "session" scope, meaning it will be executed only once per
    test session.

    Returns:
        mdb: The MongoDB connection object.
    """
    print("\n\033[32m================== Setup MongoDB ===============\033[0m")
    return mdb(
        host="192.168.0.128",
        port=27017,
        db_name="AutoRAID",
        collection_name="amd_desktop",
    )


@pytest.fixture(scope="session")
def drone(drone_api):
    """
    Fixture to set up a Raspberry Pi (presumably for drone control).

    Initializes an `rpi` object (presumably for interacting with a Raspberry
    Pi) with the specified UART parameters and drone API. This fixture has a
    "session" scope, meaning it will be executed only once per test session.

    Args:
        drone_api: The API object for interacting with the drone.

    Returns:
        rpi: The Raspberry Pi interaction object.
    """
    print("\n\033[32m================== Setup RSBPi =================\033[0m")
    return rpi(
        uart_path='/dev/ttyUSB0',
        baud_rate=115200,
        file_name='logs/uart.log',
        rpi_api=drone_api,
    )


@pytest.fixture(scope="module", autouse=True)
def test_open_uart(drone):
    """
    Fixture to automatically open and close the UART connection.

    This fixture opens the UART connection using the `drone` fixture, yields
    control to the test functions, and then closes the UART connection after
    the test functions have completed. It has a "module" scope and is
    automatically used by all tests within the module due to `autouse=True`.

    Args:
        drone: The Raspberry Pi interaction fixture.

    Yields:
        The opened UART connection.
    """
    print("\n\033[32m================== Setup UART ==================\033[0m")
    yield drone.open_uart()
    print('\n\033[32m================== Teardown UART ===============\033[0m')
    drone.close_uart()


@pytest.fixture(scope="package")
def target_system(my_app):
    """
    Fixture to set up the target system (AMD64 platform).

    Initializes an `amd64` object representing the target system, using the
    provided `my_app` interface. This fixture has a "session" scope.

    Args:
        my_app: The application interface for interacting with the target
        system.

    Returns:
        amd64: The target system object.
    """
    print("\n\033[32m================== Setup Platform ==============\033[0m")
    return amd64(interface=my_app)


@pytest.fixture(scope="package")
def amd64_windows(windows_api):
    """
    docstring
    """
    print("\n\033[32m================== Setup AMD System ============\033[0m")
    return AMD64Windows(interface=windows_api)


@pytest.fixture(scope="function")
def target_perf(target_system):
    """
    Fixture to set up performance testing on the target system.

    Creates an `amd64perf` object for performance testing, initialized with
    the `target_system` and a specified I/O file. This fixture has a function
    scope, meaning it will be executed before each test function.

    Args:
        target_system: The target system fixture.

    Returns:
        amd64perf: The performance testing object.
    """
    print("\n\033[32m================== Setup Performance ===========\033[0m")
    return amd64perf(platform=target_system, io_file="D:\\IO.dat")


@pytest.fixture(scope="function")
def target_stress(target_system):
    """Fixture to set up an AMD64MultiPathStress instance for I/O stress tests

    Args:
        target_system: The system instance to run stress tests on.

    Returns:
        AMD64MultiPathStress: Instance for executing stress test operations.
    """
    print('\n\033[32m================ Setup I/O Stress ==========\033[0m')
    return amps(platform=target_system)


@pytest.fixture(scope="package")
def win_event(target_system):
    """Fixture for setting up Windows Event monitoring for system errors.

    Args:
        target_system: The system instance to monitor for Windows Event logs.

    Returns:
        WindowsEvent: An instance of WindowsEvent for error logging.
    """
    print('\n\033[32m================== Setup Win Event =============\033[0m')
    return We(platform=target_system)


@pytest.fixture(scope="function", autouse=True)
def test_check_error(win_event):
    """Fixture to clear previous Windows event logs and check for specific
    errors after each test function.

    Yields:
        Clears event logs and checks for errors upon test completion.

    Raises:
        AssertionError: If specific errors (ID 51 or 157) are detected in logs
    """

    yield win_event.clear_error()

    errors = []
    if win_event.find_error(
        "System",
        51,
        r'An error was detected on device (\\\w+\\\w+\.+)'
    ):
        errors.append("Error 51 detected in system logs.")

    if win_event.find_error("System", 157,
                            r'Disk (\d+) has been surprise removed.'):
        errors.append("Error 157 detected: Disk surprise removal.")

    if errors:
        raise AssertionError(f"Detected errors: {errors}")

    print('\n\033[32m================== Teardown Win Event ==========\033[0m')
