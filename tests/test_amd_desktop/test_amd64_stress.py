# Contents of test_amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps
from tests.test_amd_desktop.test_amd64_perf import log_io_metrics

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

FULL_READ = 0
HALF_READ = 50
FULL_WRITE = 100
OVER_NIGHT = 30
MULTI_THREAD = 2
OPTIMAL_RR_QD = 8

class TestAMD64MultiPathStress(object):
    ''' Test I/O Stress for 8 hours
        Endurance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    @pytest.fixture(scope="function", autouse=True)
    def target_stress(self, target_system):
        print('\n\033[32m================ Setup I/O Stress ===============\033[0m')
        return amps(target_system)

    def test_run_io_operation(self, target_stress, my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_stress.run_io_operation(
            MULTI_THREAD, OPTIMAL_RR_QD, '4k', '4k', FULL_READ, OVER_NIGHT)
        
        # logger.info(f'w{FULL_READ}_stress_read_bw = {read_bw}')
        # logger.info(f'w{FULL_READ}_stress_read_iops = {read_iops}')
        # logger.info(f'w{FULL_READ}_stress_write_bw = {write_bw}')
        # logger.info(f'w{FULL_READ}_stress_write_iops = {write_iops}')
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics()

        logger.debug(f'criteria = {criteria}')

        # if (result['_id']['write_pattern'] == self.WRITE_PATTERN and
        #     result['_id']['io_depth'] == self.QUEUE_DEPTH):
        #     assert read_iops >= result['avg_read_iops'] * 0.9
        #     assert read_bw >= result['avg_read_bw'] * 0.9
        #     assert write_iops >= result['avg_write_iops'] * 0.9
        #     assert write_bw >= result['avg_write_bw'] * 0.9
        
