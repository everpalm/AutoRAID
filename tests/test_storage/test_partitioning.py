# Contents of tests/test_storage/test_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest


logger = logging.getLogger(__name__)

with open('config/test_disk_partition.json', 'r', encoding='utf-8') as f:
    SCENARIO = json.load(f)


class TestDiskVolume:
    """
    Test class for validating WindowsVolume functionalities.

    This class includes tests for script writing, partition creation,
    partition execution, and script deletion.
    """
    @pytest.mark.dependency(name="not max partitions")
    @pytest.mark.xfail
    def test_partition_existance(self, disk_partition):
        """
        Test that the partition count does not exceed the allowed number.

        Args:
            amd_system (AMD64NVMe): The NVMe target system.
            disk_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            The number of existing partitions should be less than the allowed
            number.
        """
        logger.debug("disk_info = %s", disk_partition.disk_info)
        logger.debug("partition_num = %s", disk_partition.partition_num)
        assert len(disk_partition.disk_info) < disk_partition.partition_num

    @pytest.mark.dependency(name="not system drive")
    @pytest.mark.parametrize('scenario', SCENARIO)
    def test_write_script(self, disk_partition, scenario):
        """
        Test writing and executing a script on a partition.

        Args:
            disk_partition (WindowsVolume): The WindowsVolume instance.
            scenario (dict): A test scenario from the configuration file.

        Asserts:
            Writing the script should succeed.
            Execution results should match the expected pattern.
        """
        write_result = disk_partition.write_script(scenario["Script"])
        logger.debug('write_script = %s', write_result)
        assert write_result is True

        exe_result = disk_partition.execute(scenario["Pattern"])
        logger.debug('exe_result = %s', exe_result)
        assert exe_result == scenario["Expected"]

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_create_partition(self, disk_partition):
        """
        Test creating a new partition.

        Args:
            disk_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            Partition creation should succeed.
        """
        create_result = disk_partition.create_partition()
        assert create_result is True

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_execute(self, disk_partition):
        """
        Test executing a DiskPart script on the partition.

        Args:
            disk_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            The execution result should match the expected message.
        """
        exe_result = disk_partition.execute(
            r"(DiskPart successfully formatted the volume\.)")
        logger.info('exe_result = %s', exe_result)
        assert exe_result == "DiskPart successfully formatted the volume."

    @pytest.mark.dependency(depends=["not max partitions", "not system drive"])
    def test_delete_script(self, disk_partition):
        """
        Test deleting a script from the partition.

        Args:
            disk_partition (WindowsVolume): The WindowsVolume instance.

        Asserts:
            Script deletion should succeed.
        """
        del_result = disk_partition.delete_script()
        logger.debug('del_result = %s', del_result)
        assert del_result is True

    @pytest.mark.skip(reason="Volatile")
    def test_disk_serial_number(self, disk_partition):
        """Test for verifying the number of disks and the serial number.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        target: int = disk_partition.disk_num
        logger.info("serial_number = %s",
                    disk_partition.physical_drive[target].serial_number)
        assert disk_partition.physical_drive[target].serial_number == (
            disk_partition.serial_num)

    def test_partition_size(self, disk_partition):
        """Test for verifying parition size of the disk.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        target: int = disk_partition.disk_num
        partition_size: int = disk_partition.partition_size
        logger.info("Partition Size = %d GB", partition_size)

        partitions = disk_partition.physical_drive[target].partitions
        logger.debug("paritions = %s", partitions)

        primary_partitions = [p for p in partitions if p["Type"] == "Primary"]
        logger.debug("primary_paritions = %s", primary_partitions)

        assert all(p["Size"] == "64 GB" for p in primary_partitions), (
            f"Primary partitions size less than '64 GB': {primary_partitions}"
        )

    def test_disk_capacity(self, disk_partition):
        """Test for verifying parition size of the disk.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        target: int = disk_partition.disk_num
        drive_size: int = disk_partition.physical_drive[target].size
        logger.debug("drive_size = %s", drive_size)

        disk_capacity: float = f"{disk_partition.disk_capacity} GB"
        logger.info("disk_capacity = %s", disk_capacity)
        assert disk_capacity == drive_size

    def test_get_volume(self, disk_partition, amd64_settings):
        """Test for verifying disk volume information.

        Args:
            disk_partition: The partition instance being tested.
            amd64_settings (dict): Expected configuration data for validation.
        """
        partition_num = disk_partition.partition_num
        logger.debug("partition_num = %s", partition_num)

        # 動態生成磁碟字母，跳過某些字母（例如無效或保留的磁碟字母）
        start_letter = ord('E')  # 磁碟字母起始為 'E'
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
                logger.info('%s = %s', disk_partition.disk_info[i][0],
                            disk_partition.disk_info[i][1])
            except IndexError:
                logger.error("IndexError: No disk info for partition %d", i)
                break

        # 根據動態生成的 disk_letters 驗證磁碟資訊
        for i, letter in enumerate(disk_letters):
            try:
                # 驗證磁碟資訊是否正確
                assert disk_partition.disk_info[i][1] == \
                    amd64_settings['Disk Information'][letter]
            except IndexError:
                logger.warning("IndexError: No disk info for partition %d", i)
            except KeyError:
                logger.warning("KeyError: Missing expected key: %s", letter)

    @pytest.mark.skip(reason="Tentative")
    def test_get_volume1(self, disk_partition):
        """Test for verifying disk volume information.

        Args:
            disk_partition: The partition instance being tested.
            amd64_settings (dict): Expected configuration data for validation.
        """
        target: int = disk_partition.disk_num
        partition_num: int = disk_partition.partition_num
        logger.debug("partition_num = %d", partition_num)

        # 動態生成磁碟字母，跳過某些字母（例如無效或保留的磁碟字母）
        start_letter = ord('E')  # 磁碟字母起始為 'E'
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
                logger.info('%s = %s', disk_partition.disk_info[i][0],
                            disk_partition.disk_info[i][1])
            except IndexError:
                logger.error("IndexError: No disk info for partition %d", i)
                break

        # 根據動態生成的 disk_letters 驗證磁碟資訊
        for i, letter in enumerate(disk_letters):
            try:
                # 驗證磁碟資訊是否正確
                # assert disk_partition.disk_info[i][1] == \
                logger.info(
                    "partition = %s",
                    disk_partition.physical_drive[target].partitions[i]
                )
            except IndexError:
                logger.warning("IndexError: No disk info for partition %d", i)
            except KeyError:
                logger.warning("KeyError: Missing expected key: %s", letter)
