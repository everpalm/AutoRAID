# Content of test_commandline.conftest.py
'''Copyright (c) 2025 Jaron Cheng'''
import json
import pytest
from commandline.mnv_cli import CLIFactory
# from storage.performance import PerfFactory
from storage.stress import StressFactory
from unit.mongodb import MongoDB as mdb
from amd64.system import BaseOS
from storage.partitioning import PartitionFactory
from storage.partitioning import PartitionDisk
from interface.application import BaseInterface


@pytest.fixture(scope="module")
def mnv_cli(network_api, amd64_system):
    '''docstring'''
    console = CLIFactory(network_api)
    print('\n\033[32m================== Setup Command Test ===========\033[0m')
    return console.initiate(platform=amd64_system)


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


@pytest.fixture(scope="module")
def win_partition(amd64_system: BaseOS,
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

    return partition.initiate(platform=amd64_system, disk_format='gpt',
                              file_system='ntfs')


@pytest.fixture(scope="module")
def amd64_settings():
    """Fixture to load AMD64 settings from a JSON file."""
    with open('config/rog_x570.json', 'r', encoding='utf-8') as f:
        return json.load(f)
