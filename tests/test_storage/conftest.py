# Content of tests/test_storage/conftest.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import paramiko
import pytest

# from amd64.nvme import AMD64NVMe as amd64
from system.amd64 import BaseOS
from event.logging import EventFactory
from interface.application import BaseInterface
# from interface.application_interface import ApplicationInterface as api
from storage.partitioning import PartitionDisk
from storage.partitioning import PartitionFactory
from storage.performance import PerfFactory
from storage.stress import StressFactory
from unit.mongodb import MongoDB as mdb
from system.arm import RaspberryPi

paramiko.util.log_to_file("paramiko.log", level=logging.CRITICAL)


@pytest.fixture(scope="session")
def my_mdb():
    """
    Fixture to establish a connection to a MongoDB database.

    Establishes a connection to MongoDB with the specified parameters. This
    fixture has a "session" scope, meaning it will be executed only once per
    test session.
    Database: "AutoRAID"
    Collection: "amd64"

    Returns:
        mdb: The MongoDB connection object.
    """
    print("\n\033[32m================== Setup MongoDB ===============\033[0m")
    return mdb(
        host="192.168.0.128",
        port=27017,
        db_name="AutoRAID",
        collection_name="storage",
    )


@pytest.fixture(scope="session")
def machine_learn():
    '''
    Fixture to establish a connection to a MongoDB database
    Database: "MLAutoRAID"
    Collection: "system

    Returns:
        mdb: The MongoDB connection object.
    '''
    print("\n\033[32m================== Setup Machine Learning ======\033[0m")
    return mdb(
        host="192.168.0.128",
        port=27017,
        db_name="MLAutoRAID",
        collection_name="system",
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


@pytest.fixture(scope="function")
def target_perf(amd64, cmdopt, network_api):
    """
    Fixture to set up performance testing on the target system.

    Creates an `amd64perf` object for performance testing, initialized with
    the `amd64` and a specified I/O file. This fixture has a function
    scope, meaning it will be executed before each test function.

    Args:
        amd64: The target system fixture.

    Returns:
        amd64perf: The performance testing object.
    """
    print("\n\033[32m================== Setup Performance Test ======\033[0m")
    perf = PerfFactory(api=network_api)
    return perf.initiate(platform=amd64, io_file=cmdopt.get('io_file'))


@pytest.fixture(scope="module")
def disk_partition(amd64: BaseOS,
                   network_api: BaseInterface) -> PartitionDisk:
    """
    Pytest fixture to initialize a WindowsVolume instance for testing.

    Args:
        amd_system (AMD64NVMe): The NVMe target system.

    Returns:
        WindowsVolume: An instance of the WindowsVolume class with the
        specified platform, disk format, and file system.
    """
    partition = PartitionFactory(api=network_api)
    print("\n\033[32m================== Setup Partitioning ==========\033[0m")
    return partition.initiate(platform=amd64, disk_format='gpt',
                              file_system='ntfs')


@pytest.fixture(scope="function")
def target_stress(amd64, network_api, disk_partition):
    """Fixture to set up an AMD64MultiPathStress instance for I/O stress tests

    Args:
        amd64: The system instance to run stress tests on.

    Returns:
        AMD64MultiPathStress: Instance for executing stress test operations.
    """
    print('\n\033[32m================== Setup Stress Test ===========\033[0m')
    stress = StressFactory(network_api)
    return stress.initiate(platform=amd64, diskpart=disk_partition)


@pytest.fixture(scope="package")
def os_event(amd64, network_api):
    """Fixture for setting up Windows Event monitoring for system errors.

    Args:
        amd64: The system instance to monitor for Windows Event logs.

    Returns:
        WindowsEvent: An instance of WindowsEvent for error logging.
    """
    print('\n\033[32m================== Setup Event Logging =========\033[0m')
    event = EventFactory(network_api)
    return event.initiate(platform=amd64)


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


@pytest.fixture(scope="module")
def amd64_settings():
    """Fixture to load ASUS Rog X570 settings from a JSON file."""
    with open('config/rog_x570.json', 'r', encoding='utf-8') as f:
        return json.load(f)
