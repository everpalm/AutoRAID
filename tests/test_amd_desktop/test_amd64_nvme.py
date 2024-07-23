# Contents of test_amd_64_nvme.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest

''' Set up logger '''
# logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    # datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

AMD64_NVM = (
    {
        "CPU Information":
        {
            "CPU(s)": "12-Core",
            "Model Name": "AMD Ryzen 9"
        },
        "Desktop Information":
        {
            "Manufacturer": "System",
            "Model": "System Product",
            "Name": "MY-TESTBED-01",
            "Operating System": "Windows"
        },
        "PCIE Configuration":
        {
            "Manufacturer": "NVM",
            "VID": "1B4B",
            "DID": "22411B4B",
            "SDID": "22411B4B",
            "Rev": "20"
        },
        "NVME List":
        {
            "Node": "nvme0n1",
            "SN": "00000000000000000000",
            'Model': 'Marvell_NVMe_Controller',
            'Namespace ID': '1',
            'Namespace Usage': '1.02 TB',
            'FW Rev': '10001053'
        },
        "NVME SMART-log":
        {
            "critical_warning": 0,
            "temperature": 80,
            "power_cycles": 625,
            "unsafe_shutdowns": 624
        },
        "Disk Information":
        {
            "Number": 1,
            "SerialNumber": '0050_43C5_0E00_0001.',
            "Volume": "D",
            "Size": "931.43 GB"
        }
    },
)

TEST_PATTERN = (
    {
        "Thread": 1,
        "IO Depth": 32,
        "Block Size": '4k',
        "Random Size": None,
        "Write Pattern": 50,
        "Duration": 10,
        "Test File": 'D:\\IO.dat',
        "Read IO": {
            "BW": 171.3,
            "IOPS": 43851
        },
        "Write IO": {
            "BW": 171.43,
            "IOPS": 43885.35
        },
        "CR": 0.8
    },
)


class TestAMD64NVMe(object):
    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_cpu_info(self, target_system, amd64_nvm):
        logger.info('CPU(s) = %s, CPU model = %s', target_system.cpu_num,
                    target_system.cpu_name)
        assert target_system.cpu_num == \
            amd64_nvm['CPU Information']["CPU(s)"]
        assert target_system.cpu_name == \
            amd64_nvm['CPU Information']["Model Name"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_desktop_info(self, target_system, amd64_nvm):
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    target_system.vendor,
                    target_system.model,
                    target_system.name)
        assert target_system.vendor == \
            amd64_nvm['Desktop Information']["Manufacturer"]
        assert target_system.model == \
            amd64_nvm['Desktop Information']["Model"]
        assert target_system.name == \
            amd64_nvm['Desktop Information']["Name"]
        assert target_system.os == \
            amd64_nvm['Desktop Information']["Operating System"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_pcie_info(self, target_system, amd64_nvm):
        assert target_system.vid == \
            amd64_nvm['PCIE Configuration']["VID"]
        assert target_system.did == \
            amd64_nvm['PCIE Configuration']["DID"]
        assert target_system.sdid == \
            amd64_nvm['PCIE Configuration']["SDID"]
        assert target_system.rev == \
            amd64_nvm['PCIE Configuration']["Rev"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_disk_num(self, target_system, amd64_nvm):
        # logger.debug('target_system.disk_num = ', target_system.disk_num)
        assert target_system.disk_num == \
            amd64_nvm['Disk Information']["Number"]
        assert target_system.serial_num == \
            amd64_nvm['Disk Information']["SerialNumber"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_volume(self, target_system, amd64_nvm):
        # logger.debug('target_system.node = ', target_system.node)
        # logger.debug('target_system.size = ', target_system.size)
        assert target_system.volume == \
            amd64_nvm['Disk Information']["Volume"]
        assert target_system.size == \
            amd64_nvm['Disk Information']["Size"]
 
    # @pytest.mark.repeat(3)
    @pytest.mark.parametrize('test_pattern', TEST_PATTERN)
    def test_run_io_operation(self, target_system, test_pattern):
        read_bw, read_iops, write_bw, write_iops = \
            target_system.run_io_operation(
                test_pattern["Thread"],
                test_pattern["IO Depth"],
                test_pattern["Block Size"],
                test_pattern["Random Size"],
                test_pattern["Write Pattern"],
                test_pattern["Duration"],
                test_pattern["Test File"]
        )
        assert read_bw >= \
            test_pattern["Read IO"]["BW"] * test_pattern["CR"]
        assert read_iops >= \
            test_pattern["Read IO"]["IOPS"] * test_pattern["CR"]
        assert write_bw >= \
            test_pattern["Write IO"]["BW"] * test_pattern["CR"]
        assert write_iops >= \
            test_pattern["Write IO"]["IOPS"] * test_pattern["CR"]
        