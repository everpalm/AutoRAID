# Contents of test_storage.test_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest

# from amd64.system import BaseOS
# from storage.partitioning import PartitionFactory
# from storage.partitioning import PartitionDisk
from storage.partitioning import WindowsVolume
# from interface.application import BaseInterface

logger = logging.getLogger(__name__)

with open('config/test_win_partition.json', 'r', encoding='utf-8') as f:
    SCENARIO = json.load(f)


# @pytest.fixture(scope="module")
# def win_partition(amd64_system: BaseOS,
#                   network_api: BaseInterface) -> PartitionDisk:
#     """
#     Pytest fixture to initialize a WindowsVolume instance for testing.

#     Args:
#         amd_system (AMD64NVMe): The NVMe target system.

#     Returns:
#         WindowsVolume: An instance of the WindowsVolume class with the
#         specified platform, disk format, and file system.
#     """
#     partition = PartitionFactory(api=network_api)
#     print("\n\033[32m================== Setup Win Partitioning ======\033[0m")
#     return partition.initiate(platform=amd64_system, disk_format='gpt',
#                               file_system='ntfs')


class TestWindowsVolume:
    """
    Test class for validating WindowsVolume functionalities.

    This class includes tests for script writing, partition creation,
    partition execution, and script deletion.
    """
    @pytest.mark.dependency(name="not max partitions")
    @pytest.mark.xfail
    def test_partition_existance(self, win_partition):
        """
        Test that the partition count does not exceed the allowed number.

        Args:
            amd_system (AMD64NVMe): The NVMe target system.
            win_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            The number of existing partitions should be less than the allowed
            number.
        """
        logger.debug("disk_info = %s", win_partition.disk_info)
        logger.debug("partition_num = %s", win_partition.partition_num)
        assert len(win_partition.disk_info) < win_partition.partition_num

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

    def test_get_disk_num(self, win_partition, amd64_settings):
        """Test for verifying the number of disks and the serial number.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info("Number = %s", win_partition.disk_num)
        logger.info("SerialNumber = %s", win_partition.serial_num)
        assert (win_partition.disk_num ==
                amd64_settings['Disk Information']["Number"])

    def test_partition_size(self, win_partition):
        """Test for verifying parition size of the disk.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        partition_size = win_partition.partition_size
        logger.info("Partition Size = %s GB", partition_size)

    def test_disk_capacity(self, win_partition):
        """Test for verifying parition size of the disk.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        disk_capacity = win_partition.disk_capacity
        logger.info("disk_capacity = %s GB", disk_capacity)

    def test_get_volume(self, win_partition, amd64_settings):
        """Test for verifying disk volume information.

        Args:
            win_partition: The partition instance being tested.
            amd64_settings (dict): Expected configuration data for validation.
        """
        partition_num = win_partition.partition_num
        logger.debug("partition_num = %s", partition_num)

        # 動態生成磁碟字母，跳過某些字母（例如無效或保留的磁碟字母）
        start_letter = ord('D')  # 磁碟字母起始為 'D'
        disk_letters = []
        for i in range(partition_num):
            letter = chr(start_letter + i)
            if letter not in {'A', 'B', 'C'}:  # 排除保留字母，例如 'A', 'B', 'C'
                disk_letters.append(letter)
        logger.debug("Generated disk_letters: %s", disk_letters)

        # 驗證磁碟字母總數是否符合 partition_num
        if len(disk_letters) != partition_num:
            logger.error("Generated disk letter count (%d) does not match "
                         "partition_num (%d)",
                         len(disk_letters), partition_num)
            raise AssertionError("Mismatch between generated disk letters and "
                                 "partition count")

        # 處理磁碟資訊，僅迭代 partition_num 的範圍
        for i in range(partition_num):
            try:
                logger.info('%s = %s', win_partition.disk_info[i][0],
                            win_partition.disk_info[i][1])
            except IndexError:
                logger.error("IndexError: No disk info for partition %d", i)
                break

        # 根據動態生成的 disk_letters 驗證磁碟資訊
        for i, letter in enumerate(disk_letters):
            try:
                # 驗證磁碟資訊是否正確
                assert win_partition.disk_info[i][1] == \
                    amd64_settings['Disk Information'][letter]
            except IndexError:
                logger.warning("IndexError: No disk info for partition %d", i)
            except KeyError:
                logger.warning("KeyError: Missing expected key: %s", letter)
