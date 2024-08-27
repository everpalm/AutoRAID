# Contents of test_amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)


class TestAMD64MultiPathStress(object):
    ''' Test I/O Stress for 8 hours
        Endurance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    WRITE_PATTERN = 0
    DURATION = 120

    @pytest.fixture(scope="module", autouse=True)
    def target_stress(self, target_system):
        print('\n\033[32m================ Setup I/O Stress ===============\033[0m')
        # return amps(target_system, 50, 30)
        return amps(target_system)

    def test_run_io_operation(self, target_stress, my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_stress.run_io_operation(
            2, 8, '4k', '4k', self.WRITE_PATTERN, self.DURATION)
        
        logger.info(f'w{self.WRITE_PATTERN}_stress_read_bw = {read_bw}')
        logger.info(f'w{self.WRITE_PATTERN}_stress_read_iops = {read_iops}')
        logger.info(f'w{self.WRITE_PATTERN}_stress_write_bw = {write_bw}')
        logger.info(f'w{self.WRITE_PATTERN}_stress_write_iops = {write_iops}')
        
        # result = my_mdb.aggregate_random_metrics(self.WRITE_PATTERN,
        #                                         self.QUEUE_DEPTH)
        # # logger.debug(f'write_pattern = {write_pattern}')
        # # logger.debug(f'io_depth = {io_depth}')
        # logger.debug(f'result = {result}')

        # if (result['_id']['write_pattern'] == self.WRITE_PATTERN and
        #     result['_id']['io_depth'] == self.QUEUE_DEPTH):
        #     assert read_iops >= result['avg_read_iops'] * 0.9
        #     assert read_bw >= result['avg_read_bw'] * 0.9
        #     assert write_iops >= result['avg_write_iops'] * 0.9
        #     assert write_bw >= result['avg_write_bw'] * 0.9

