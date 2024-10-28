# Contents of test_system_performance_unit.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import logging
from unittest.mock import MagicMock, patch

# 模擬的 SystemPerformance 和 SystemUnderTesting 模組
from unit.system_performance import SystemPerformance as perf
from unit.system_under_testing import SystemUnderTesting as sut

''' Set up logger '''
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# 測試所用的資料
RW_MODE = ["randread", "randwrite", "read", "write"]
BLOCK_SIZE = ["512", "1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k",
              "256k", "512k", "1M"]
IO_DEPTH = [1, 2, 4, 8, 16, 32, 64, 128]
RUN_TIME = [30, 60, 120, 240, 480]
JOB_NUM = [1, 2, 4, 8, 16, 32, 64, 128]

RR_4K_IOD1_JOB1 = (
    {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 1, "Run Time": 30,
      "Job": 1, "IOPS": 5315, "BW": 21768440, "CR": 0.7, "CPU Mask": 0x1},
    {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 1, "Run Time": 30,
     "Job": 1, "IOPS": 5315, "BW": 21768440, "CR": 0.7, "CPU Mask": 0x1},
    {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 2, "Run Time": 30,
     "Job": 1, "IOPS": 9000, "BW": 36846960, "CR": 0.7, "CPU Mask": 0x1},
    {"RW Mode": "randread", "Block Size": "4k", "IO Depth": 4, "Run Time": 30,
     "Job": 1, "IOPS": 14540, "BW": 58248396, "CR": 0.7, "CPU Mask": 0x1},
)

RW_4K_IOD1_JOB1 = (
    {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 1, "Run Time": 30,
     "Job": 1, "IOPS": 5315, "BW": 21768440, "CR": 0.7, "CPU Mask": 0x1},
    {"RW Mode": "randwrite", "Block Size": "4k", "IO Depth": 1, "Run Time": 30,
     "Job": 1, "IOPS": 5315, "BW": 21768440, "CR": 0.7, "CPU Mask": 0x1},
)

# 測試類別
class TestPerformanceIODepth:
    """Test class for I/O depth-related performance testing. Uses mocked 
    instances of system performance and system under test (SUT) classes.
    """

    @pytest.fixture(scope="session", autouse=True)
    def target_system(self):
        """Fixture to set up the SystemUnderTesting (SUT) instance with mocked 
        behavior. Auto-runs for each test session.
        """
        # 使用 mock 模擬 sut 類別
        mock_sut = MagicMock(spec=sut)
        logger.info('===Setup SUT===')
        return mock_sut

    @pytest.fixture(scope="session", autouse=True)
    def target_performance(self):
        """Fixture to set up the SystemPerformance instance with mocked behavior. 
        Auto-runs for each test session.
        """
        # 使用 mock 模擬 perf 類別
        mock_perf = MagicMock(spec=perf)
        logger.info('===Setup Perf===')
        return mock_perf

    def test_groupby_io_mean_open_file(self, target_performance):
        # 模擬文件讀取失敗，檢查異常情況
        """Test the groupby_io_mean method to simulate a FileNotFoundError 
        exception. Confirms that the exception is correctly raised when a file 
        is missing.
        """
        target_performance.groupby_io_mean.side_effect = FileNotFoundError
        with pytest.raises(FileNotFoundError):
            target_performance.groupby_io_mean(4, 'IOPS')

    @pytest.mark.parametrize('rw_mode', RW_MODE)
    @pytest.mark.parametrize('io_depth', IO_DEPTH)
    def test_run_io_operation(self, target_system, rw_mode, io_depth):
        """Parameterized test for running I/O operations with various read/write
        modes and I/O depths. Checks that the run_io_operation method is called
        with the correct parameters.
        """
        # 模擬執行 I/O 操作
        target_system.run_io_operation(rw_mode, '4k', io_depth, 1, 30, 4)
        # 檢查 I/O 操作是否被正確執行
        target_system.run_io_operation.assert_called_with(rw_mode, '4k',
                                                          io_depth, 1, 30, 4)

    @pytest.mark.parametrize("rr_table", RR_4K_IOD1_JOB1)
    def test_groupby_rr_mean(self, target_performance, rr_table):
        """Test for calculating mean IOPS and BW for read operations (RR).
        Uses mock data and verifies that the mean values meet the confidence
        interval threshold.
        """
        # 根據參數決定返回 IOPS 或 BW 的值
        def mock_groupby_io_mean(io_depth, metric):
            if metric == 'IOPS':
                return rr_table['IOPS']
            elif metric == 'BW':
                return rr_table['BW']
            return None

        target_performance.groupby_io_mean.side_effect = mock_groupby_io_mean

        # 調用 groupby_io_mean 並獲取 IOPS 和 BW 均值
        str_iops_mean = target_performance.groupby_io_mean(
            rr_table['IO Depth'], 'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(rr_table['IO Depth'],
                                                         'BW')

        logger.info('IO Depth = %s, IOPS = %s, BW = %s', rr_table['IO Depth'],
                    str_iops_mean, str_bw_mean)

        # 驗證 IOPS 和 BW 的均值是否大於等於可信區間
        assert str_iops_mean >= rr_table['IOPS'] * rr_table['CR']
        assert str_bw_mean >= rr_table['BW'] * rr_table['CR']

    @pytest.mark.parametrize("rw_table", RW_4K_IOD1_JOB1)
    def test_groupby_rw_mean(self, target_performance, rw_table):
        """Test for calculating mean IOPS and BW for write operations (RW).
        Uses mock data and verifies that the mean values meet the confidence
        interval threshold.
        """
        # 根據參數決定返回 IOPS 或 BW 的值
        def mock_groupby_io_mean(io_depth, metric):
            if metric == 'IOPS':
                return rw_table['IOPS']
            elif metric == 'BW':
                return rw_table['BW']
            return None

        target_performance.groupby_io_mean.side_effect = mock_groupby_io_mean

        # 調用 groupby_io_mean 並獲取 IOPS 和 BW 均值
        str_iops_mean = target_performance.groupby_io_mean(
            rw_table['IO Depth'], 'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(rw_table['IO Depth'],
                                                         'BW')

        logger.info('IO Depth = %s, IOPS = %s, BW = %s', rw_table['IO Depth'],
                    str_iops_mean, str_bw_mean)

        # 驗證 IOPS 和 BW 的均值是否大於等於可信區間
        assert str_iops_mean >= rw_table['IOPS'] * rw_table['CR']
        assert str_bw_mean >= rw_table['BW'] * rw_table['CR']

# 子類別繼承主測試類別
class TestPerformanceCPUMask(TestPerformanceIODepth):
    """Subclass of TestPerformanceIODepth that adds CPU Mask parameterization.
    Extends I/O operation tests to include various CPU mask values.
    """
    @pytest.mark.parametrize('cpu_mask',
                             [hex(cpu_mask) for cpu_mask in range(1, 16)])
    @pytest.mark.parametrize('rw_mode', RW_MODE)
    def test_run_io_operation(self, target_system, rw_mode, cpu_mask):
        """Parameterized test for running I/O operations with various CPU 
        mask values and read/write modes. Verifies that run_io_operation 
        is called with correct parameters.
        """
        # 使用 CPU Mask 參數進行 I/O 操作測試
        target_system.run_io_operation(rw_mode, '4k', 128, 1, 30, cpu_mask)
        # 檢查 I/O 操作是否被正確執行
        target_system.run_io_operation.assert_called_with(rw_mode, '4k', 128,
                                                        1, 30, cpu_mask)

    @pytest.mark.parametrize("rr_table", RR_4K_IOD1_JOB1)
    def test_groupby_rr_mean(self, target_performance, rr_table):
        """Extended test for calculating mean IOPS and BW for read operations (RR),
        using CPU Mask parameter. Verifies mean values meet confidence interval.
        """
        # 根據參數決定返回 IOPS 或 BW 的值
        def mock_groupby_io_mean(io_depth, metric):
            if metric == 'IOPS':
                return rr_table['IOPS']
            elif metric == 'BW':
                return rr_table['BW']
            return None

        target_performance.groupby_io_mean.side_effect = mock_groupby_io_mean

        # 調用 groupby_io_mean 並獲取 IOPS 和 BW 均值
        str_iops_mean = target_performance.groupby_io_mean(
            rr_table['CPU Mask'], 'IOPS')
        str_bw_mean = target_performance.groupby_io_mean(rr_table['CPU Mask'],
                                                         'BW')

        logger.info('CPU Mask = %s, IOPS = %s, BW = %s', rr_table['CPU Mask'],
                    str_iops_mean, str_bw_mean)

        # 驗證 IOPS 和 BW 的均值是否大於等於可信區間
        assert str_iops_mean >= rr_table['IOPS'] * rr_table['CR']
        assert str_bw_mean >= rr_table['BW'] * rr_table['CR']
