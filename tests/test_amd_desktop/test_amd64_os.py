# Contents of test_amd64_os.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest

# Set up logger
logger = logging.getLogger(__name__)

with open('config/amd64_nvme.json', 'r', encoding='utf-8') as f:
    AMD64_SETTINGS = [json.load(f)]


class TestAMD64System:
    '''Duplicate of TestAMD64NVMe'''
    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_hyperthreading(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying hyperthreading setting.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info("hyperthreading = %s", amd64_system.hyperthreading)
        assert (amd64_system.hyperthreading ==
                AMD64_SETTINGS['CPU Information']['Hyperthreading'])

    def test_memory_size(self, amd64_system):
        """Test for verifying memory size of the system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        memory_size = amd64_system.memory_size
        logger.info("Memory Size = %s GB", memory_size)

    # @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_mac_address(self, amd64_system):
        """Test for verifying MAC address of the system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        mac_address = amd64_system.mac_address
        logger.info("MAC Address = %s", mac_address)

    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_cpu_info(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying CPU model and core count.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('CPU(s) = %s, CPU model = %s', amd64_system.cpu_num,
                    amd64_system.cpu_name)
        assert (amd64_system.cpu_num ==
                AMD64_SETTINGS['CPU Information']["CPU(s)"])
        assert (amd64_system.cpu_name ==
                AMD64_SETTINGS['CPU Information']["Model Name"])

    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_desktop_info(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    amd64_system.vendor,
                    amd64_system.model,
                    amd64_system.name)
        assert (amd64_system.vendor ==
                AMD64_SETTINGS['Desktop Information']["Manufacturer"])
        assert (amd64_system.model ==
                AMD64_SETTINGS['Desktop Information']["Model"])

    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_pcie_info(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying PCIe configuration, including VID, DID, SDID,
        and Rev.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('VID = %s', amd64_system.vid)
        logger.info('DID = %s', amd64_system.did)
        logger.info('SDID = %s', amd64_system.sdid)
        logger.info('Rev = %s', amd64_system.rev)

        assert (amd64_system.vid ==
                AMD64_SETTINGS['PCIE Configuration']["VID"])
        assert (amd64_system.did ==
                AMD64_SETTINGS['PCIE Configuration']["DID"])
        assert (amd64_system.sdid ==
                AMD64_SETTINGS['PCIE Configuration']["SDID"])
        assert (amd64_system.rev ==
                AMD64_SETTINGS['PCIE Configuration']["Rev"])

    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_disk_num(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying the number of disks and the serial number.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info("Number = %s", amd64_system.disk_num)
        logger.info("SerialNumber = %s", amd64_system.serial_num)
        assert (amd64_system.disk_num ==
                AMD64_SETTINGS['Disk Information']["Number"])

    @pytest.mark.parametrize('AMD64_SETTINGS', AMD64_SETTINGS)
    def test_get_volume(self, amd64_system, AMD64_SETTINGS):
        """Test for verifying disk volume information.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        for i in range(12):  # 迴圈處理 0 到 11
            try:
                logger.info('%s = %s', amd64_system.disk_info[i][0],
                            amd64_system.disk_info[i][1])
            except IndexError:
                break  # 如果索引超出範圍，則跳出迴圈

        disk_letters = ["D", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
                        "P"]
        for i, letter in enumerate(disk_letters):
            try:
                assert amd64_system.disk_info[i][1] == \
                    AMD64_SETTINGS['Disk Information'][letter]
            except (IndexError, KeyError):  # 處理索引或鍵錯誤
                pass  # 或是選擇其他處理方式，例如記錄錯誤訊息

    def test_partition_size(self, amd64_system):
        """Test for verifying parition size of the disk.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        partition_size = amd64_system.partition_size
        logger.info("Partition Size = %s GB", partition_size)

    def test_disk_capacity(self, amd64_system):
        """Test for verifying parition size of the disk.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        disk_capacity = amd64_system.disk_capacity
        logger.info("disk_capacity = %s", disk_capacity)
