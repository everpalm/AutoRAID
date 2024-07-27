# Contents of amd64_performance.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import logging
import os
from tests.test_amd_desktop.test_amd64_nvme import TestAMD64NVMe as nvm

logger = logging.getLogger(__name__)

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


class TestRandomReadWrite(nvm):
    ''' Test AMD64 Performance
        Performance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    @pytest.mark.parametrize('io_depth', [2**power for power in range(1)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_system, write_pattern, io_depth, my_mdb):
    # def test_run_io_operation(self, target_system, my_mdb):
        # read_bw, read_iops, write_bw, write_iops = target_system.run_io_operation(1,32,'4k','4k',0,10,'D:\\IO.dat')
        target_system.run_io_operation(1, io_depth, '4k', '4k', write_pattern,
            10, 'D:\\IO.dat')
        result = my_mdb.aggregate_metrics()
        print(f'result = {result}')
        # for doc in result:
        #     print(f'doc = {doc}')
            # for key, value in doc.items():
            #     logger.debug(f'result = {key}: {value}')
        # assert read_bw >= \
        #     test_pattern["Read IO"]["BW"] * test_pattern["CR"]
        # assert read_iops >= \
        #     test_pattern["Read IO"]["IOPS"] * test_pattern["CR"]
        # assert write_bw >= \
        #     test_pattern["Write IO"]["BW"] * test_pattern["CR"]
        # assert write_iops >= \
        #     test_pattern["Write IO"]["IOPS"] * test_pattern["CR"]