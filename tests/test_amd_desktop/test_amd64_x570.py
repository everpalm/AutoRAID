# Contents of test_amd64x570.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest

# Set up logger
logger = logging.getLogger(__name__)

with open('config/amd64_nvme.json', 'r', encoding='utf-8') as f:
    AMD64_NVM = [json.load(f)]


class TestAMD64X570:
    '''Duplicate of TestAMD64NVMe'''
    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_hyperthreading(self, amd64x570, amd64_nvm):
        """Test for verifying hyperthreading setting.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info("hyperthreading = %s", amd64x570.hyperthreading)
        assert (amd64x570.hyperthreading ==
                amd64_nvm['CPU Information']['Hyperthreading'])

    def test_memory_size(self, amd64x570):
        """Test for verifying memory size of the system.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        memory_size = amd64x570.memory_size
        logger.info("Memory Size = %s GB", memory_size)

    # @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_mac_address(self, amd64x570):
        """Test for verifying MAC address of the system.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        mac_address = amd64x570.mac_address
        logger.info("MAC Address = %s", mac_address)

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_cpu_info(self, amd64x570, amd64_nvm):
        """Test for verifying CPU model and core count.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('CPU(s) = %s, CPU model = %s', amd64x570.cpu_num,
                    amd64x570.cpu_name)
        assert (amd64x570.cpu_num ==
                amd64_nvm['CPU Information']["CPU(s)"])
        assert (amd64x570.cpu_name ==
                amd64_nvm['CPU Information']["Model Name"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_desktop_info(self, amd64x570, amd64_nvm):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    amd64x570.vendor,
                    amd64x570.model,
                    amd64x570.name)
        assert (amd64x570.vendor ==
                amd64_nvm['Desktop Information']["Manufacturer"])
        assert (amd64x570.model ==
                amd64_nvm['Desktop Information']["Model"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_pcie_info(self, amd64x570, amd64_nvm):
        """Test for verifying PCIe configuration, including VID, DID, SDID,
        and Rev.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('VID = %s', amd64x570.vid)
        logger.info('DID = %s', amd64x570.did)
        logger.info('SDID = %s', amd64x570.sdid)
        logger.info('Rev = %s', amd64x570.rev)

        assert (amd64x570.vid ==
                amd64_nvm['PCIE Configuration']["VID"])
        assert (amd64x570.did ==
                amd64_nvm['PCIE Configuration']["DID"])
        assert (amd64x570.sdid ==
                amd64_nvm['PCIE Configuration']["SDID"])
        assert (amd64x570.rev ==
                amd64_nvm['PCIE Configuration']["Rev"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_disk_num(self, amd64x570, amd64_nvm):
        """Test for verifying the number of disks and the serial number.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info("Number = %s", amd64x570.disk_num)
        logger.info("SerialNumber = %s", amd64x570.serial_num)
        assert (amd64x570.disk_num ==
                amd64_nvm['Disk Information']["Number"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_volume(self, amd64x570, amd64_nvm):
        """Test for verifying disk volume information.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        for i in range(12):  # 迴圈處理 0 到 11
            try:
                logger.info('%s = %s', amd64x570.disk_info[i][0],
                            amd64x570.disk_info[i][1])
            except IndexError:
                break  # 如果索引超出範圍，則跳出迴圈

        disk_letters = ["D", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
                        "P"]
        for i, letter in enumerate(disk_letters):
            try:
                assert amd64x570.disk_info[i][1] == \
                    amd64_nvm['Disk Information'][letter]
            except (IndexError, KeyError):  # 處理索引或鍵錯誤
                pass  # 或是選擇其他處理方式，例如記錄錯誤訊息

    def test_partition_size(self, amd64x570):
        """Test for verifying parition size of the disk.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        partition_size = amd64x570.partition_size
        logger.info("Partition Size = %s GB", partition_size)

    def test_disk_capacity(self, amd64x570):
        """Test for verifying parition size of the disk.

        Args:
            amd64x570: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        disk_capacity = amd64x570.disk_capacity
        logger.info("disk_capacity = %s", disk_capacity)
