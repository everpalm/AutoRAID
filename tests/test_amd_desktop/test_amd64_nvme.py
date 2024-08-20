# Contents of test_amd_64_nvme.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
import json

PROJECT_PATH = "/home/pi/Projects/AutoRAID"

''' Set up logger '''
# logging.getLogger(__name__).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

with open(f'{PROJECT_PATH}/config/amd64_nvme.json', 'r') as f:
    AMD64_NVM = [json.load(f)]

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
            "BW": 105,
            "IOPS": 26920
        },
        "Write IO": {
            "BW": 105,
            "IOPS": 26972
        },
        "CR": 0.8
    },
)


class TestAMD64NVMe(object):
    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_mac_address(self, target_system, amd64_nvm):
        mac_address = target_system.mac_address
        logger.info(f'MAC Address = {mac_address}')

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
        # assert target_system.name == \
        #     amd64_nvm['Desktop Information']["Name"]
        assert target_system.os == \
            amd64_nvm['Desktop Information']["Operating System"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_pcie_info(self, target_system, amd64_nvm):
        logger.info(f'VID = {target_system.vid}')
        logger.info(f'DID = {target_system.did}')
        logger.info(f'SDID = {target_system.sdid}')
        logger.info(f'Rev = {target_system.rev}')
        
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
        logger.info(f'Number = {target_system.disk_num}')
        logger.info(f'SerialNumber = {target_system.serial_num}')
        assert target_system.disk_num == \
            amd64_nvm['Disk Information']["Number"]
        assert target_system.serial_num == \
            amd64_nvm['Disk Information']["SerialNumber"]

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_volume(self, target_system, amd64_nvm):
        logger.info(f'Volume = {target_system.volume}')
        logger.info(f'Size = {target_system.size}')
        assert target_system.volume == \
            amd64_nvm['Disk Information']["Volume"]
        assert target_system.size == \
            amd64_nvm['Disk Information']["Size"]
 
    # @pytest.mark.repeat(3)
    # @pytest.mark.parametrize('test_pattern', TEST_PATTERN)
    # def test_run_io_operation(self, target_system, test_pattern):
    #     read_bw, read_iops, write_bw, write_iops = \
    #         target_system.run_io_operation(
    #             test_pattern["Thread"],
    #             test_pattern["IO Depth"],
    #             test_pattern["Block Size"],
    #             test_pattern["Random Size"],
    #             test_pattern["Write Pattern"],
    #             test_pattern["Duration"],
    #             test_pattern["Test File"]
    #     )
    #     logger.info(f'read_bw = {read_bw}')
    #     logger.info(f'read_iops = {read_iops}')
    #     logger.info(f'write_bw = {write_bw}')
    #     logger.info(f'write_iops = {write_iops}')
        
    #     assert read_bw >= \
    #         test_pattern["Read IO"]["BW"] * test_pattern["CR"]
    #     assert read_iops >= \
    #         test_pattern["Read IO"]["IOPS"] * test_pattern["CR"]
    #     assert write_bw >= \
    #         test_pattern["Write IO"]["BW"] * test_pattern["CR"]
    #     assert write_iops >= \
    #         test_pattern["Write IO"]["IOPS"] * test_pattern["CR"]
        