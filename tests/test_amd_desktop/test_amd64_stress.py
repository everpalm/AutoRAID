# Contents of test_amd64_stress.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from amd_desktop.amd64_stress import AMD64MultiPathStress as amps
from tests.test_amd_desktop.test_amd64_perf import log_io_metrics

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)

FULL_READ = 0
OLTP_LOADING = 30 # With 8 KB chunk size
FULL_WRITE = 100
OVER_NIGHT = 156
HYPER_THREAD = 2
SINGLE_THREAD = 1
MIN_IODEPTH = 1
MAX_IODEPTH = 33
OPTIMUM_IODEPTH = 7

class TestAMD64MultiPathStress(object):
    ''' Test I/O Stress 
        Endurance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in
            advance
    '''
    # @pytest.fixture(scope="function", autouse=True)
    @pytest.fixture(scope="function")
    def target_stress(self, target_system):
        print('\n\033[32m================ Setup I/O Stress ==========\033[0m')
        return amps(platform=target_system)

    @pytest.mark.parametrize('iodepth', list(range(MIN_IODEPTH, MAX_IODEPTH)))
    @pytest.mark.parametrize('write_pattern', [FULL_READ, FULL_WRITE])
    def test_run_io_operation(self, target_stress, write_pattern, iodepth,
                              my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_stress.run_io_operation(
            SINGLE_THREAD, iodepth, '4k', '4k', write_pattern, OVER_NIGHT)
    
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'stress_')

        criteria = my_mdb.aggregate_stress_metrics(write_pattern, iodepth)

        logger.debug(f'criteria = {criteria}')
        
