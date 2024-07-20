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


RW_TABLE = (
                {
                    "Thread": 1,
                    "IO Depth": 32,
                    "Block Size": '4k',
                    "Random Size": None,
                    "Write Pattern": 50,
                    "Duration": 10,
                    "Test File": 'D:\IO.dat',
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
    @pytest.mark.parametrize('rw_table', RW_TABLE)
    def test_run_io_operation(self, target_system, rw_table):
        dic_perf = target_system.run_io_operation(
            rw_table["Thread"],
            rw_table["IO Depth"],
            rw_table["Block Size"],
            rw_table["Random Size"],
            rw_table["Write Pattern"],
            rw_table["Duration"],
            rw_table["Test File"]
        )
        assert dic_perf["Read IO"]["BW"] >= \
            rw_table["Read IO"]["BW"] * rw_table["CR"]
        assert dic_perf["Read IO"]["IOPS"] >= \
            rw_table["Read IO"]["IOPS"] * rw_table["CR"]
        assert dic_perf["Write IO"]["BW"] >= \
            rw_table["Write IO"]["BW"] * rw_table["CR"]
        assert dic_perf["Write IO"]["IOPS"] >= \
            rw_table["Write IO"]["IOPS"] * rw_table["CR"]
        # logger.debug(f'Read IO BW = {df_perf["Read IO"]["BW"]}')
        # logger.debug(f'Read IO PS = {df_perf["Read IO"]["IOPS"]}')
        # logger.debug(f'Write IO BW = {df_perf["Write IO"]["BW"]}')
        # logger.debug(f'Write IO PS = {df_perf["Write IO"]["IOPS"]}')
    #     df_perf = target_system.run_io_operation(
    #             rw_table['RW Mode'],
    #             rw_table['Block Size'],
    #             rw_table['IO Depth'],
    #             rw_table['Job'],
    #             rw_table['Run Time'],
    #             rw_table['CPU Mask'])
    #     # Check if IOPS is greater or equal to pass credible region
    #     assert df_perf.iloc[-1, 0] >= rw_table['IOPS'] * rw_table['CR']
    #     # Check if bandwidth is greater or equal to pass credible region
    #     assert df_perf.iloc[-1, 1] >= rw_table['BW'] * rw_table['CR']

    # @pytest.mark.parametrize("rw_table", RW_TABLE)
    # def test_groupby_io_mean(self, target_system, rw_table):
    #     str_iops_mean = target_system.groupby_io_mean(
    #                 'my_data.json',
    #                 'IO Depth',
    #                 rw_table['IO Depth'],
    #                 'IOPS')
    #     str_bw_mean = target_system.groupby_io_mean(
    #                 'my_data.json',
    #                 'IO Depth',
    #                 rw_table['IO Depth'],
    #                 'BW')
    #     logger.info('IO Depth = %s, IOPS = %s, BW = %s',
    #                 rw_table['IO Depth'], str_iops_mean, str_bw_mean)
    #     # Check if IOPS is greater or equal to pass credible region
    #     assert str_iops_mean >= rw_table['IOPS'] * rw_table['CR']
    #     # Check if bandwidth is greater or equal to pass credible region
    #     assert str_bw_mean >= rw_table['BW'] * rw_table['CR']

    # def test_groupby_io_mean_open_file(self, target_system):
    #     with pytest.raises(FileNotFoundError):
    #         target_system.groupby_io_mean(
    #                 'stub.json',
    #                 'IO Depth',
    #                 4,
    #                 'IOPS')
# if __name__ == '__main__':
# pytest.main(['test_system_under_testing.py', '-s', '-v', '-x'])