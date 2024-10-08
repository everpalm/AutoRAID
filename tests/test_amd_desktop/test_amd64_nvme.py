# Contents of test_amd_64_nvme.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
import json

# PROJECT_PATH = "/home/pi/Projects/AutoRAID"

''' Set up logger '''
logger = logging.getLogger(__name__)

# with open(f'{PROJECT_PATH}/config/amd64_nvme.json', 'r') as f:
with open('config/amd64_nvme.json', 'r') as f:
    AMD64_NVM = [json.load(f)]

# TEST_PATTERN = (
#     {
#         "Thread": 1,
#         "IO Depth": 32,
#         "Block Size": '4k',
#         "Random Size": None,
#         "Write Pattern": 50,
#         "Duration": 10,
#         "Test File": 'D:\\IO.dat',
#         "Read IO": {
#             "BW": 105,
#             "IOPS": 26920
#         },
#         "Write IO": {
#             "BW": 105,
#             "IOPS": 26972
#         },
#         "CR": 0.8
#     },
# )


class TestAMD64NVMe(object):
    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_hyperthreading(self, target_system, amd64_nvm):
        logger.info(f'hyperthreading = {target_system.hyperthreading}')
        assert (target_system.hyperthreading == 
            amd64_nvm['CPU Information']['Hyperthreading'])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_memory_size(self, target_system, amd64_nvm):
        memory_size = target_system.memory_size
        logger.info(f'Memory Size = {memory_size} GB')

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_mac_address(self, target_system, amd64_nvm):
        mac_address = target_system.mac_address
        logger.info(f'MAC Address = {mac_address}')

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_cpu_info(self, target_system, amd64_nvm):
        logger.info('CPU(s) = %s, CPU model = %s', target_system.cpu_num,
                    target_system.cpu_name)
        assert (target_system.cpu_num ==
            amd64_nvm['CPU Information']["CPU(s)"])
        assert (target_system.cpu_name ==
            amd64_nvm['CPU Information']["Model Name"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_desktop_info(self, target_system, amd64_nvm):
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
        logger.info(f'VID = {target_system.vid}')
        logger.info(f'DID = {target_system.did}')
        logger.info(f'SDID = {target_system.sdid}')
        logger.info(f'Rev = {target_system.rev}')
        
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
        logger.info(f'Number = {target_system.disk_num}')
        logger.info(f'SerialNumber = {target_system.serial_num}')
        assert (target_system.disk_num ==
            amd64_nvm['Disk Information']["Number"])

    @pytest.mark.parametrize('amd64_nvm', AMD64_NVM)
    def test_get_volume(self, target_system, amd64_nvm):
        logger.info(f'{target_system.disk_info[0][0]} = '
              f'{target_system.disk_info[0][1]}')
        logger.info(f'{target_system.disk_info[1][0]} = '
              f'{target_system.disk_info[1][1]}')
        logger.info(f'{target_system.disk_info[2][0]} = '
              f'{target_system.disk_info[2][1]}')
        logger.info(f'{target_system.disk_info[3][0]} = '
              f'{target_system.disk_info[3][1]}')
        logger.info(f'{target_system.disk_info[4][0]} = '
              f'{target_system.disk_info[4][1]}')
        logger.info(f'{target_system.disk_info[5][0]} = '
              f'{target_system.disk_info[5][1]}')
        logger.info(f'{target_system.disk_info[6][0]} = '
              f'{target_system.disk_info[6][1]}')
        logger.info(f'{target_system.disk_info[7][0]} = '
              f'{target_system.disk_info[7][1]}')
        logger.info(f'{target_system.disk_info[8][0]} = '
              f'{target_system.disk_info[8][1]}')
        logger.info(f'{target_system.disk_info[9][0]} = '
              f'{target_system.disk_info[9][1]}')
        logger.info(f'{target_system.disk_info[10][0]} = '
              f'{target_system.disk_info[10][1]}')
        logger.info(f'{target_system.disk_info[11][0]} = '
              f'{target_system.disk_info[11][1]}')
        
        assert (target_system.disk_info[0][1] ==
            amd64_nvm['Disk Information']["D"])
        assert (target_system.disk_info[1][1] ==
            amd64_nvm['Disk Information']["F"])
        assert (target_system.disk_info[2][1] ==
            amd64_nvm['Disk Information']["G"])
        assert (target_system.disk_info[3][1] ==
            amd64_nvm['Disk Information']["H"])
        assert (target_system.disk_info[4][1] ==
            amd64_nvm['Disk Information']["I"])
        assert (target_system.disk_info[5][1] ==
            amd64_nvm['Disk Information']["J"])
        assert (target_system.disk_info[6][1] ==
            amd64_nvm['Disk Information']["K"])
        assert (target_system.disk_info[7][1] ==
            amd64_nvm['Disk Information']["L"])
        assert (target_system.disk_info[8][1] ==
            amd64_nvm['Disk Information']["M"])
        assert (target_system.disk_info[9][1] ==
            amd64_nvm['Disk Information']["N"])
        assert (target_system.disk_info[10][1] ==
            amd64_nvm['Disk Information']["O"])
        assert (target_system.disk_info[11][1] ==
            amd64_nvm['Disk Information']["P"])
 
        