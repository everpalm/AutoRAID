# Contents of test_system_performance.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
from unit.system_performance import SystemPerformance as perf
from unit.system_under_testing import SystemUnderTesting as sut

''' Set up logger '''
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

RW_MODE = ["randread", "randwrite", "read", "write"]
BLOCK_SIZE = ["512", "1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k",
              "256k", "512k", "1M"]
IO_DEPTH = [1, 2, 4, 8, 16, 32, 64, 128]
RUN_TIME = [30, 60, 120, 240, 480]
JOB_NUM = [1, 2, 4, 8, 16, 32, 64, 128]

RR_4K_IOD1_JOB1 = (
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 30, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 30, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 2,
                    "Run Time": 30, "Job": 1, "IOPS": 9000, "BW": 36846960,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 4,
                    "Run Time": 30, "Job": 1, "IOPS": 14540, "BW": 58248396,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 8,
                    "Run Time": 30, "Job": 1, "IOPS": 36198, "BW": 144703488,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 16,
                    "Run Time": 30, "Job": 1, "IOPS": 69376, "BW": 279445504,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 32,
                    "Run Time": 30, "Job": 1, "IOPS": 97715, "BW": 390856700,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 64,
                    "Run Time": 30, "Job": 1, "IOPS": 105199, "BW": 419954700,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 128,
                    "Run Time": 30, "Job": 1, "IOPS": 111104, "BW": 443547600,
                    "CR": 0.7, "CPU Mask": 0x1}
            )

RW_4K_IOD1_JOB1 = (
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 30, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 1,
                    "Run Time": 30, "Job": 1, "IOPS": 5315, "BW": 21768440,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 2,
                    "Run Time": 30, "Job": 1, "IOPS": 9000, "BW": 36846960,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 4,
                    "Run Time": 30, "Job": 1, "IOPS": 14540, "BW": 58248396,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 8,
                    "Run Time": 30, "Job": 1, "IOPS": 36198, "BW": 144703488,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 16,
                    "Run Time": 30, "Job": 1, "IOPS": 69376, "BW": 279445504,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 32,
                    "Run Time": 30, "Job": 1, "IOPS": 97715, "BW": 390856700,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 64,
                    "Run Time": 30, "Job": 1, "IOPS": 105199, "BW": 419954700,
                    "CR": 0.7, "CPU Mask": 0x1},
                {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 128,
                    "Run Time": 30, "Job": 1, "IOPS": 111104, "BW": 443547600,
                    "CR": 0.7, "CPU Mask": 0x1}
            )


class TestPerformanceIODepth(object):
    @pytest.fixture(scope="session", autouse=True)
    def target_system(self):
        logger.info('===Setup SUT===')
        return sut('Marvell')

    @pytest.fixture(scope="session", autouse=True)
    def target_performance(self):
        logger.info('===Setup Perf===')
        return perf('my_data.json', 'IO Depth')

    @pytest.fixture(scope="function", autouse=False)
    def stub_file(self):
        logger.info('===Setup Stub===')
        yield perf('stub.json', 'IO Depth')
        logger.info('===Teardown Stub===')

    def test_groupby_io_mean_open_file(self, stub_file):
        with pytest.raises(FileNotFoundError):
            stub_file.groupby_io_mean(4, 'IOPS')

    # @pytest.mark.repeat(3)
    @pytest.mark.parametrize('rw_mode', RW_MODE)
    @pytest.mark.parametrize('io_depth', IO_DEPTH)
    def test_run_io_operation(self, target_system, rw_mode, io_depth):
        target_system.run_io_operation(rw_mode, '4k', io_depth, 1, 30, 4)

    @pytest.mark.skip(reason="Group by MongoDB instead")
    @pytest.mark.parametrize("rr_table", RR_4K_IOD1_JOB1)
    def test_groupby_rr_mean(self, target_performance, rr_table):
        str_iops_mean = target_performance.groupby_io_mean(
                    rr_table['IO Depth'],
                    'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(
                    rr_table['IO Depth'],
                    'BW')
        logger.info('IO Depth = %s, IOPS = %s, BW = %s',
                    rr_table['IO Depth'], str_iops_mean, str_bw_mean)
        # Check if IOPS is greater or equal to pass credible region
        assert str_iops_mean >= rr_table['IOPS'] * rr_table['CR']
        # Check if bandwidth is greater or equal to pass credible region
        assert str_bw_mean >= rr_table['BW'] * rr_table['CR']

    @pytest.mark.skip(reason="Group by MongoDB instead")
    @pytest.mark.parametrize("rw_table", RW_4K_IOD1_JOB1)
    def test_groupby_rw_mean(self, target_performance, rw_table):
        str_iops_mean = target_performance.groupby_io_mean(
                    rw_table['IO Depth'],
                    'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(
                    rw_table['IO Depth'],
                    'BW')
        logger.info('IO Depth = %s, IOPS = %s, BW = %s',
                    rw_table['IO Depth'], str_iops_mean, str_bw_mean)
        # Check if IOPS is greater or equal to pass credible region
        assert str_iops_mean >= rw_table['IOPS'] * rw_table['CR']
        # Check if bandwidth is greater or equal to pass credible region
        assert str_bw_mean >= rw_table['BW'] * rw_table['CR']


class TestPerformanceCPUMask(TestPerformanceIODepth):
    @pytest.mark.parametrize('cpu_mask', [hex(cpu_mask) for cpu_mask in
                                          range(1, 16)])
    @pytest.mark.parametrize('rw_mode', RW_MODE)
    def test_run_io_operation(self, target_system, rw_mode, cpu_mask):
        target_system.run_io_operation(rw_mode, '4k', 128, 1, 30, cpu_mask)

    @pytest.mark.parametrize("rr_table", RR_4K_IOD1_JOB1)
    def test_groupby_rr_mean(self, target_performance, rr_table):
        str_iops_mean = target_performance.groupby_io_mean(
                    rr_table['CPU Mask'],
                    'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(
                    rr_table['CPU Mask'],
                    'BW')
        logger.info('CPU Mask = %s, IOPS = %s, BW = %s',
                    rr_table['CPU Mask'], str_iops_mean, str_bw_mean)
        # Check if IOPS is greater or equal to pass credible region
        assert str_iops_mean >= rr_table['IOPS'] * rr_table['CR']
        # Check if bandwidth is greater or equal to pass credible region
        assert str_bw_mean >= rr_table['BW'] * rr_table['CR']
# if __name__ == '__main__':
# pytest.main(['test_system_under_testing.py', '-s', '-v', '-x'])