# Content of tests/test_amd64/conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import paramiko
import pytest

from event.logging import EventFactory
# from amd64.nvme import AMD64NVMe as amd64
# from amd64.system import PlatformFactory
from storage.performance import PerfFactory
from storage.stress import StressFactory
from interface.application_interface import ApplicationInterface as api
from unit.mongodb import MongoDB as mdb
from arm.system import RaspberryPi

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)


@pytest.fixture(scope="session")
def my_app(cmdopt):
    '''
    Initialize and return an API interface for the test session.

    This fixture sets up an API interface for the test environment based on
    the configuration provided in the `cmdopt` parameter. It is marked as
    deprecated and should be replaced with newer implementations in the future

    Args:
        cmdopt (dict): A dictionary containing configuration options for the
        API interface.
            - os_type (str): The operating system type (e.g., 'Windows',
            'Linux').
            - mode (str): The mode in which the interface operates (e.g.,
            'test', 'production').
            - if_name (str): The name of the interface to be used.
            - config_file (str): The path to the configuration file.

    Returns:
        Interface: An instance of the API interface created based on the
        provided configuration.

    Notes:
        - This setup method is marked as deprecated.
        - The green-highlighted setup message indicates that this API is
        obsolete.
    '''
    print('\n\033[32m================== Setup API (Deprecated)=======\033[0m')
    return api.create_interface(
        os_type=cmdopt.get('os_type'),
        mode=cmdopt.get('mode'),
        if_name=cmdopt.get('if_name'),
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
def drone(raspi_interface):
    """
    Fixture to set up a Raspberry Pi (presumably for drone control).

    Initializes an `Raspberry` object (presumably for interacting with a
    Raspberry Pi) with the specified UART parameters and drone API. This
    fixture has a "session" scope, meaning it will be executed only once per
    test session.

    Args:
        drone_api: The API object for interacting with the drone.

    Returns:
        RaspberryPi: The Raspberry Pi interaction object.
    """
    print("\n\033[32m================== Setup RPi System ============\033[0m")
    return RaspberryPi(
        uart_path='/dev/ttyUSB0',
        baud_rate=115200,
        file_name='logs/uart.log',
        rpi_api=raspi_interface,
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


# @pytest.fixture(scope="session")
# def target_system(my_app):
#     """
#     Fixture to set up the target system (AMD64 platform).

#     Initializes an `amd64` object representing the target system, using the
#     provided `my_app` interface. This fixture has a "session" scope.

#     Args:
#         my_app: The application interface for interacting with the target
#         system.

#     Returns:
#         amd64: The target system object.
#     """
#    print("\n\033[32m================== Setup Platform (Deprecated)==\033[0m")
#     # platform = PlatformFactory(api=my_app)
#     return amd64(interface=my_app)


@pytest.fixture(scope="function")
def target_perf(amd64_system, cmdopt, network_api):
    """
    Fixture to set up performance testing on the target system.

    Creates an `amd64perf` object for performance testing, initialized with
    the `amd64_system` and a specified I/O file. This fixture has a function
    scope, meaning it will be executed before each test function.

    Args:
        amd64_system: The target system fixture.

    Returns:
        amd64perf: The performance testing object.
    """
    print("\n\033[32m================== Setup Performance Test ======\033[0m")
    perf = PerfFactory(api=network_api)
    return perf.initiate(platform=amd64_system, io_file=cmdopt.get('io_file'))


@pytest.fixture(scope="function")
def target_stress(amd64_system, network_api):
    """Fixture to set up an AMD64MultiPathStress instance for I/O stress tests

    Args:
        amd64_system: The system instance to run stress tests on.

    Returns:
        AMD64MultiPathStress: Instance for executing stress test operations.
    """
    print('\n\033[32m================== Setup Stress Test ===========\033[0m')
    stress = StressFactory(network_api)
    return stress.initiate(platform=amd64_system)


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
