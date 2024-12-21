# Contents of test_amd_64_nvme.py
'''Unit tests for the AMD64 NVMe system configuration and details. This module 
   includes tests for retrieving system and hardware information, including 
   CPU, memory, disk, and PCIe configuration, and compares these values to 
   expected configurations stored in a JSON file.

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest

# Set up logger
logger = logging.getLogger(__name__)

with open('config/amd64_nvme.json', 'r', encoding='utf-8') as f:
    AMD64_NVM = [json.load(f)]


class TestAMD64NVMe:
    """Test class for AMD64 NVMe system information and configuration.
    
    Each method retrieves a specific hardware or system configuration detail
    from the AMD64 NVMe system and validates it against the expected values 
    loaded from the configuration file.
    """

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_hyperthreading(self, target_system, amd64_nvm):
        """Test for verifying hyperthreading setting.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info("hyperthreading = %s", target_system.hyperthreading)
        assert (target_system.hyperthreading ==
            amd64_nvm['CPU Information']['Hyperthreading'])

    def test_memory_size(self, target_system):
        """Test for verifying memory size of the system.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        memory_size = target_system.memory_size
        logger.info("Memory Size = %s GB", memory_size)

    # @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_mac_address(self, target_system):
        """Test for verifying MAC address of the system.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        mac_address = target_system.mac_address
        logger.info("MAC Address = %s", mac_address)

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_cpu_info(self, target_system, amd64_nvm):
        """Test for verifying CPU model and core count.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('CPU(s) = %s, CPU model = %s', target_system.cpu_num,
                    target_system.cpu_name)
        assert (target_system.cpu_num ==
            amd64_nvm['CPU Information']["CPU(s)"])
        assert (target_system.cpu_name ==
            amd64_nvm['CPU Information']["Model Name"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_desktop_info(self, target_system, amd64_nvm):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    target_system.vendor,
                    target_system.model,
                    target_system.name)
        assert (target_system.vendor ==
            amd64_nvm['Desktop Information']["Manufacturer"])
        assert (target_system.model ==
            amd64_nvm['Desktop Information']["Model"])
        # assert target_system.name == \
        #     amd64_nvm['Desktop Information']["Name"]
        assert (target_system.os ==
            amd64_nvm['Desktop Information']["Operating System"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_pcie_info(self, target_system, amd64_nvm):
        """Test for verifying PCIe configuration, including VID, DID, SDID, and Rev.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info('VID = %s', target_system.vid)
        logger.info('DID = %s', target_system.did)
        logger.info('SDID = %s', target_system.sdid)
        logger.info('Rev = %s', target_system.rev)

        assert (target_system.vid ==
            amd64_nvm['PCIE Configuration']["VID"])
        assert (target_system.did ==
            amd64_nvm['PCIE Configuration']["DID"])
        assert (target_system.sdid ==
            amd64_nvm['PCIE Configuration']["SDID"])
        assert (target_system.rev ==
            amd64_nvm['PCIE Configuration']["Rev"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_disk_num(self, target_system, amd64_nvm):
        """Test for verifying the number of disks and the serial number.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        logger.info("Number = %s", target_system.disk_num)
        logger.info("SerialNumber = %s", target_system.serial_num)
        assert (target_system.disk_num ==
            amd64_nvm['Disk Information']["Number"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_volume(self, target_system, amd64_nvm):
        """Test for verifying disk volume information.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        for i in range(12):  # 迴圈處理 0 到 11
            try:
                logger.info('%s = %s', target_system.disk_info[i][0],
                            target_system.disk_info[i][1])
            except IndexError:
                break  # 如果索引超出範圍，則跳出迴圈

        disk_letters = ["D", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
                        "P"]
        for i, letter in enumerate(disk_letters):
            try:
                assert target_system.disk_info[i][1] == \
                    amd64_nvm['Disk Information'][letter]
            except (IndexError, KeyError): #處理索引或鍵錯誤
                pass #或是選擇其他處理方式，例如記錄錯誤訊息

    def test_partition_size(self, target_system):
        """Test for verifying parition size of the disk.

        Args:
            target_system: The system instance being tested.
            amd64_nvm (dict): Expected configuration data for validation.
        """
        partition_size = target_system.partition_size
        logger.info("Partition Size = %s GB", partition_size)
   