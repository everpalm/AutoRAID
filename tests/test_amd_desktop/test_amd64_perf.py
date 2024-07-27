# Contents of amd64_performance.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import logging
import os
from tests.test_amd_desktop.test_amd64_nvme import TestAMD64NVMe as nvm

logger = logging.getLogger(__name__)


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
    def test_run_io_operation(self, target_system, write_pattern, io_depth,
        my_mdb):
    # def test_run_io_operation(self, target_system, my_mdb):
        # read_bw, read_iops, write_bw, write_iops = target_system.run_io_operation(1,32,'4k','4k',0,10,'D:\\IO.dat')
        read_bw, read_iops, write_bw, write_iops = \
            target_system.run_io_operation(1, io_depth, '4k', '4k',
                write_pattern, 10, 'D:\\IO.dat')
        logger.info(f'read_bw = {read_bw}')
        logger.info(f'read_iops = {read_iops}')
        logger.info(f'write_bw = {write_bw}')
        logger.info(f'write_iops = {write_iops}')
        
        result = my_mdb.aggregate_metrics(write_pattern, io_depth)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'io_depth = {io_depth}')
        logger.debug(f'result = {result}')
        # for doc in result:
        #     print(f'doc = {doc}')
            # for key, value in doc.items():
            #     logger.debug(f'result = {key}: {value}')
        if result['_id']['write_pattern'] == write_pattern and \
            result['_id']['io_depth'] == io_depth:
            assert read_iops >= result['avg_read_iops'] * 0.9
            assert read_bw >= result['avg_read_bw'] * 0.9
            assert write_iops >= result['avg_write_iops'] * 0.9
            assert write_bw >= result['avg_write_bw'] * 0.9
            
        # assert read_iops >= \
        #     test_pattern["Read IO"]["IOPS"] * test_pattern["CR"]
        # assert write_bw >= \
        #     test_pattern["Write IO"]["BW"] * test_pattern["CR"]
        # assert write_iops >= \
        #     test_pattern["Write IO"]["IOPS"] * test_pattern["CR"]