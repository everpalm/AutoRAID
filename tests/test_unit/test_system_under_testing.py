# Contents of test_system_under_testing.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
# import time
from unit.system_under_testing import SystemUnderTesting as sut

''' Set up logger '''
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
# logging.getLogger(__name__).setLevel(logging.DEBUG)

GENERIC_X86 = (
            {
                "CPU Information":
                {
                    "CPU(s)": "4",
                    "Model Name": "Intel(R) Core(TM) i5-7500 CPU @ 3.40GHz"
                },
                "Desktop Information":
                {
                    "Version": "ThinkCentre M910t"
                },
                "PCIE Configuration":
                {
                    "Manufacturer": "Marvell",
                    "SDID": "2241",
                    "BDF": '01:00.0',
                    'Vendor ID': '1414',
                    'Serial Number': '1234-5678-abcd-ef'
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
                }
            },
)


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

@pytest.mark.skip(reason="Skipping this test class")
class TestSystemUnderTesting(object):
    # @pytest.fixture(scope="session", autouse=True)
    @pytest.fixture(scope="function", autouse=True)
    def target_system(self, mocker, generic_x86):
        logger.info('===Setup SUT===')
        marvell_sut = sut('Marvell')
        marvell_sut.cpu_num = mocker.MagicMock(
            return_value=generic_x86['CPU Information']["CPU(s)"])
        marvell_sut.cpu_name = mocker.MagicMock(
            return_value=generic_x86['CPU Information']["Model Name"])
        marvell_sut.bdf = mocker.MagicMock(
            return_value=generic_x86['PCIE Configuration']["BDF"])
        marvell_sut.sdid = mocker.MagicMock(
            return_value=generic_x86['PCIE Configuration']["SDID"])
        marvell_sut.version = mocker.MagicMock(
            return_value=generic_x86['Desktop Information']["Version"])
        marvell_sut.os = mocker.MagicMock(return_value='Linux')
        marvell_sut.node = mocker.MagicMock(
            return_value=generic_x86['NVME List']["Node"])
        marvell_sut.model = mocker.MagicMock(
            return_value=generic_x86['NVME List']["Model"])
        marvell_sut.namespace_usage = mocker.MagicMock(
            return_value=generic_x86['NVME List']["Namespace Usage"])
        marvell_sut.namespace_id = mocker.MagicMock(
            return_value=generic_x86['NVME List']["Namespace ID"])
        marvell_sut.fw_rev = mocker.MagicMock(
            return_value=generic_x86['NVME List']["FW Rev"])
        marvell_sut.critical_warning = mocker.MagicMock(
            return_value=generic_x86['NVME SMART-log']["critical_warning"])
        marvell_sut.temperature = mocker.MagicMock(
            return_value=generic_x86['NVME SMART-log']["temperature"])
        marvell_sut.power_cycles = mocker.MagicMock(
            return_value=generic_x86['NVME SMART-log']["power_cycles"])
        marvell_sut.unsafe_shutdowns = mocker.MagicMock(
            return_value=generic_x86['NVME SMART-log']["unsafe_shutdowns"])
        return marvell_sut

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_cpu_info(self, target_system, generic_x86):
        logger.info('CPU(s) = %s, CPU model = %s', target_system.cpu_num(),
                    target_system.cpu_name())
        assert target_system.cpu_num() == \
            generic_x86['CPU Information']["CPU(s)"]
        assert target_system.cpu_name() == \
            generic_x86['CPU Information']["Model Name"]

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_desktop_info(self, target_system, generic_x86):
        logger.info('Version = %s', target_system.version())
        assert target_system.version() == \
            generic_x86['Desktop Information']["Version"]

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_pcie_info(self, target_system, generic_x86):
        assert target_system.bdf() == generic_x86['PCIE Configuration']["BDF"]
        assert target_system.sdid() == generic_x86['PCIE Configuration']["SDID"]

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_os(self, target_system):
        logger.info('my_sut.os = %s', target_system.os())
        assert target_system.os() == 'Linux'

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_nvme_device(self, target_system, generic_x86):
        assert target_system.node() == generic_x86['NVME List']["Node"]
        assert target_system.model() == generic_x86['NVME List']["Model"]
        assert target_system.namespace_usage() == \
            generic_x86['NVME List']["Namespace Usage"]
        assert target_system.namespace_id() == \
            generic_x86['NVME List']["Namespace ID"]
        assert target_system.fw_rev() == generic_x86['NVME List']["FW Rev"]

    @pytest.mark.parametrize('generic_x86', GENERIC_X86)
    def test_get_nvme_smart_log(self, target_system, generic_x86):
        assert target_system.critical_warning() == \
            generic_x86['NVME SMART-log']["critical_warning"]
        assert target_system.temperature() <= \
            generic_x86['NVME SMART-log']["temperature"]
        assert target_system.power_cycles() >= \
            generic_x86['NVME SMART-log']["power_cycles"]
        assert target_system.unsafe_shutdowns() >= \
            generic_x86['NVME SMART-log']["unsafe_shutdowns"]

    # # @pytest.mark.repeat(3)
    @pytest.mark.parametrize('rw_table', RW_TABLE)
    def test_run_io_operation(self, target_system, rw_table):
        df_perf = target_system.run_io_operation(
                rw_table['RW Mode'],
                rw_table['Block Size'],
                rw_table['IO Depth'],
                rw_table['Job'],
                rw_table['Run Time'],
                rw_table['CPU Mask'])
        # Check if IOPS is greater or equal to pass credible region
        assert df_perf.iloc[-1, 0] >= rw_table['IOPS'] * rw_table['CR']
        # Check if bandwidth is greater or equal to pass credible region
        assert df_perf.iloc[-1, 1] >= rw_table['BW'] * rw_table['CR']