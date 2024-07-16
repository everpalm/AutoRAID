# Contents of test_amd_64_nvme.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest

''' Set up logger '''
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

AMD64_NVM = [
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
            }
]


RW_TABLE = (
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 10, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 2,
                    "Run Time": 10, "Job": 1, "IOPS": 9000, "BW": 36846960,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 4,
                    "Run Time": 10, "Job": 1, "IOPS": 14540, "BW": 58248396,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 8,
                    "Run Time": 10, "Job": 1, "IOPS": 36198, "BW": 144703488,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 16,
                    "Run Time": 10, "Job": 1, "IOPS": 44953, "BW": 179306496,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 32,
                    "Run Time": 10, "Job": 1, "IOPS": 63692, "BW": 254803968,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 64,
                    "Run Time": 10, "Job": 1, "IOPS": 105199, "BW": 419954700,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 128,
                    "Run Time": 10, "Job": 1, "IOPS": 111104, "BW": 443547600,
                    "CR": 0.7, "CPU Mask": 4},
                # End of Random Read
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 10, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 2,
                    "Run Time": 10, "Job": 1, "IOPS": 9000, "BW": 36846960,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 4,
                    "Run Time": 10, "Job": 1, "IOPS": 14540, "BW": 58248396,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 8,
                    "Run Time": 10, "Job": 1, "IOPS": 36198, "BW": 144703488,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 16,
                    "Run Time": 10, "Job": 1, "IOPS": 63078, "BW": 279445504,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 32,
                    "Run Time": 10, "Job": 1, "IOPS": 62771, "BW": 253755392,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 64,
                    "Run Time": 10, "Job": 1, "IOPS": 63385, "BW": 248512512,
                    "CR": 0.7, "CPU Mask": 4},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 128,
                    "Run Time": 10, "Job": 1, "IOPS": 63795, "BW": 250609664,
                    "CR": 0.7, "CPU Mask": 4}
                # End of Random Write
                # {"RW Mode": "randrw", "Block Size": "4K", "IO Depth": 1,
                #   "Run Time": 10, "Job": 1, "IOPS": 20000, "BW": 8000000},
                # {"RW Mode": "read", "Block Size": "4K", "IO Depth": 1,
                #   "Run Time": 10, "Job": 1, "IOPS": 50000, "BW": 200000000},
                # {"RW Mode": "write", "Block Size": "4K", "IO Depth": 1,
                #   "Run Time": 10, "Job": 1, "IOPS": 40000, "BW": 150000000}
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
    # @pytest.mark.parametrize('rw_table', RW_TABLE)
    # def test_run_io_operation(self, target_system, rw_table):
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