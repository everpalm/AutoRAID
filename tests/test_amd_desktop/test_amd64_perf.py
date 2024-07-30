# Contents of amd64_performance.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import logging
import os
from tests.test_amd_desktop.test_amd64_nvme import TestAMD64NVMe as nvm

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TestRandomReadWrite(nvm):
    ''' Test AMD64 NVM Random Read Write Performance
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
        read_bw, read_iops, write_bw, write_iops = \
            target_system.run_io_operation(1, io_depth, '4k', '4k',
                write_pattern, 60, 'D:\\IO.dat')
        logger.info(f'random_read_bw = {read_bw}')
        logger.info(f'random_read_iops = {read_iops}')
        logger.info(f'random_write_bw = {write_bw}')
        logger.info(f'random_write_iops = {write_iops}')
        
        result = my_mdb.aggregate_random_metrics(write_pattern, io_depth)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'io_depth = {io_depth}')
        logger.debug(f'result = {result}')

        if result['_id']['write_pattern'] == write_pattern and \
            result['_id']['io_depth'] == io_depth:
            assert read_iops >= result['avg_read_iops'] * 0.9
            assert read_bw >= result['avg_read_bw'] * 0.9
            assert write_iops >= result['avg_write_iops'] * 0.9
            assert write_bw >= result['avg_write_bw'] * 0.9


class TestSequentialReadWrite(nvm):
    ''' Test AMD64 NVM Sequential Read Write Performance
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
        read_bw, read_iops, write_bw, write_iops = \
            target_system.run_io_operation(1, io_depth, '4k', None,
                write_pattern, 60, 'D:\\IO.dat')
        logger.info(f'sequential_read_bw = {read_bw}')
        logger.info(f'sequential_read_iops = {read_iops}')
        logger.info(f'sequential_write_bw = {write_bw}')
        logger.info(f'sequential_write_iops = {write_iops}')
        
        result = my_mdb.aggregate_sequential_metrics(write_pattern,
            io_depth)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'io_depth = {io_depth}')
        logger.debug(f'result = {result}')

        if result['_id']['write_pattern'] == write_pattern and \
            result['_id']['io_depth'] == io_depth:
            assert read_iops >= result['avg_read_iops'] * 0.9
            assert read_bw >= result['avg_read_bw'] * 0.9
            assert write_iops >= result['avg_write_iops'] * 0.9
            assert write_bw >= result['avg_write_bw'] * 0.9


ramp_times = list(range(10, 60, 10))


class TestRampTimeReadWrite(nvm):
    ''' Test AMD64 NVM Sequential Read Write Performance
        Performance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    @pytest.mark.parametrize('ramp_times', ramp_times)
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_system, write_pattern, ramp_times,
        my_mdb):
        read_bw, read_iops, write_bw, write_iops = \
            target_system.run_io_operation(1, 4, '4k', '4k',
                write_pattern, ramp_times, 'D:\\IO.dat')
        logger.info(f'ramp_read_bw = {read_bw}')
        logger.info(f'ramp_read_iops = {read_iops}')
        logger.info(f'ramp_write_bw = {write_bw}')
        logger.info(f'ramp_write_iops = {write_iops}')

        result = my_mdb.aggregate_ramp_metrics(write_pattern,
            ramp_times)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'ramp_times = {ramp_times}')
        logger.debug(f'result = {result}')

        # if result['_id']['write_pattern'] == write_pattern and \
        #     result['_id']['ramp_times'] == ramp_times:
        #     assert read_iops >= result['avg_read_iops'] * 0.9
        #     assert read_bw >= result['avg_read_bw'] * 0.9
        #     assert write_iops >= result['avg_write_iops'] * 0.9
        #     assert write_bw >= result['avg_write_bw'] * 0.9