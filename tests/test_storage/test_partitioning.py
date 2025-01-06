# Contents of test_win_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest

from amd_desktop.amd64_system import BaseOS
from storage.partitioning import PartitionFactory
from storage.partitioning import PartitionDisk
from storage.partitioning import WindowsVolume
from unit.amd64_interface import BaseInterface

logger = logging.getLogger(__name__)

with open('config/test_win_partition.json', 'r', encoding='utf-8') as f:
    SCENARIO = json.load(f)


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


class TestWindowsVolume:
    """
    Test class for validating WindowsVolume functionalities.

    This class includes tests for script writing, partition creation,
    partition execution, and script deletion.
    """
    @pytest.mark.dependency(name="not max partitions")
    @pytest.mark.xfail
    def test_partition_existance(self, amd64_system, win_partition):
        """
        Test that the partition count does not exceed the allowed number.

        Args:
            amd_system (AMD64NVMe): The NVMe target system.
            win_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            The number of existing partitions should be less than the allowed
            number.
        """
        assert len(amd64_system.disk_info) < win_partition.partition_num

    @pytest.mark.dependency(name="not system drive")
    @pytest.mark.parametrize('scenario', SCENARIO)
    def test_write_script(self, win_partition: WindowsVolume, scenario):
        """
        Test writing and executing a script on a partition.

        Args:
            win_partition (WindowsVolume): The WindowsVolume instance.
            scenario (dict): A test scenario from the configuration file.

        Asserts:
            Writing the script should succeed.
            Execution results should match the expected pattern.
        """
        write_result = win_partition.write_script(
            scenario["Script"])
        logger.info('write_script = %s', write_result)
        assert write_result is True

        exe_result = win_partition.execute(scenario["Pattern"])
        logger.info('exe_result = %s', exe_result)
        assert exe_result == scenario["Expected"]

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_create_partition(self, win_partition: WindowsVolume):
        """
        Test creating a new partition.

        Args:
            win_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            Partition creation should succeed.
        """
        create_result = win_partition.create_partition()
        assert create_result is True

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_execute(self, win_partition: WindowsVolume):
        """
        Test executing a DiskPart script on the partition.

        Args:
            win_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            The execution result should match the expected message.
        """
        exe_result = win_partition.execute(
            r"(DiskPart successfully formatted the volume\.)")
        logger.info('exe_result = %s', exe_result)
        assert exe_result == "DiskPart successfully formatted the volume."

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_delete_script(self, win_partition: WindowsVolume):
        """
        Test deleting a script from the partition.

        Args:
            win_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            Script deletion should succeed.
        """
        del_result = win_partition.delete_script()
        logger.info('del_result = %s', del_result)
        assert del_result is True
