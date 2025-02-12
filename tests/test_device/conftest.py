# Content of tests/test_device/test_1b4b_2241.py
'''Copyright (c) 2025 Jaron Cheng'''
import pytest

from system.amd64 import BaseOS
from system.amd64 import BaseInterface
from commandline.mnv_cli import CLIFactory
from device.changlong import BeidouFactory
from storage.partitioning import PartitionFactory
from storage.partitioning import PartitionDisk
from storage.stress import StressFactory
from unit.mongodb import MongoDB


@pytest.fixture(scope="function")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


@pytest.fixture(scope="function")
def boot_device(network_api, mnv_cli):
    '''docstring'''
    target = BeidouFactory(network_api)
    print('\n\033[32m================== Setup Device Test ===========\033[0m')
    return target.initiate(command=mnv_cli)


@pytest.fixture(scope="function")
def disk_partition(amd64_system: BaseOS,
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
    print("\n\033[32m================== Setup Win Partitioning ======\033[0m")
    return partition.initiate(platform=amd64_system, disk_format='gpt',
                              file_system='ntfs')


@pytest.fixture(scope="function")
def target_stress(amd64_system, network_api, disk_partition):
    """Fixture to set up an AMD64MultiPathStress instance for I/O stress tests

    Args:
        amd64_system: The system instance to run stress tests on.

    Returns:
        AMD64MultiPathStress: Instance for executing stress test operations.
    """
    print('\n\033[32m================== Setup Stress Test ===========\033[0m')
    stress = StressFactory(network_api)
    return stress.initiate(platform=amd64_system, diskpart=disk_partition)


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
    return MongoDB(
        host="192.168.0.128",
        port=27017,
        db_name="AutoRAID",
        collection_name="device",
    )
