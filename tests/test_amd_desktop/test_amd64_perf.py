# Contents of amd64_performance.py
'''Copyright (c) 2024 Jaron Cheng'''
import pytest
import logging
import os

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

CF_LEVEL = 6

def log_target_limit(upper_iops, lower_iops, upper_bw, lower_bw, prefix=""):
    logger.debug(f'upper_{prefix}iops = {upper_iops}')
    logger.debug(f'lower_{prefix}iops = {lower_iops}')
    logger.debug(f'upper_{prefix}bw = {upper_bw}')
    logger.debug(f'lower_{prefix}bw = {lower_bw}')

def log_io_metrics(read_bw, read_iops, write_bw, write_iops, prefix=""):
    logger.info(f'{prefix}read_bw = {read_bw}')
    logger.info(f'{prefix}read_iops = {read_iops}')
    logger.info(f'{prefix}write_bw = {write_bw}')
    logger.info(f'{prefix}write_iops = {write_iops}')

def validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria):
    if read_iops and read_bw:
        max_read_iops = criteria['max_read_iops']
        min_read_iops = criteria['min_read_iops']
        std_dev_read_iops = criteria['std_dev_read_iops']

        deviation = std_dev_read_iops * CF_LEVEL
        upper_limit_read_iops = max_read_iops + deviation
        lower_limit_read_iops = min_read_iops - deviation
        
        max_read_bw = criteria['max_read_bw']
        min_read_bw = criteria['min_read_bw']
        std_dev_read_bw = criteria['std_dev_read_bw']

        deviation = std_dev_read_bw * CF_LEVEL
        upper_limit_read_bw = max_read_bw + deviation
        lower_limit_read_bw = min_read_bw - deviation

        log_target_limit(upper_limit_read_iops, lower_limit_read_iops,
                        upper_limit_read_bw, lower_limit_read_bw, 'read_')
        
        assert upper_limit_read_iops > read_iops > lower_limit_read_iops
        assert upper_limit_read_bw > read_bw > lower_limit_read_bw

    if write_iops and write_bw:
        max_write_iops = criteria['max_write_iops']
        min_write_iops = criteria['min_write_iops']
        std_dev_write_iops = criteria['std_dev_write_iops']

        deviation = std_dev_write_iops * CF_LEVEL
        upper_limit_write_iops = max_write_iops + deviation 
        lower_limit_write_iops = min_write_iops - deviation
        
        max_write_bw = criteria['max_write_bw']
        min_write_bw = criteria['min_write_bw']
        std_dev_write_bw = criteria['std_dev_write_bw']
    
        deviation = std_dev_write_bw * CF_LEVEL
        upper_limit_write_bw = max_write_bw + deviation
        lower_limit_write_bw = min_write_bw - deviation

        log_target_limit(upper_limit_write_iops, lower_limit_write_iops,
                        upper_limit_write_bw, lower_limit_write_bw, 'write_')
       
        assert upper_limit_write_iops > write_iops > lower_limit_write_iops
        assert upper_limit_write_bw > write_bw > lower_limit_write_bw

class TestRandomReadWrite(object):
    ''' Test AMD64 NVM Random Read Write Performance
        Performance of the AMD64 system
        Attributes:
            write_pattern: 0 - full read, 100 - full write
            io_depth: power of two. Min 1, max 32
            flaky: Max try 3 times, delay 60 secounds
    # '''
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('io_depth', [2**power for power in range(6)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, io_depth, my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_perf.run_io_operation(
            io_depth, '4k', '4k', write_pattern, 156)
      
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'random_')
        
        criteria = my_mdb.aggregate_random_metrics(write_pattern, io_depth)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'io_depth = {io_depth}')
        logger.debug(f'result = {criteria}')

        validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria)

class TestSequentialReadWrite(object):
    ''' Test AMD64 NVM Sequential Read Write Performance
        Performance of the AMD64 system
        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    # @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('block_size', [f'{2**pwr}k' for pwr in range(2,8)])
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, block_size,
        my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_perf.run_io_operation(
            32, block_size, None, write_pattern, 156)
        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'sequential_')
    
        criteria = my_mdb.aggregate_sequential_metrics(write_pattern, block_size)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'block_size = {block_size}')
        logger.debug(f'criteria = {criteria}')

        validate_metrics(read_bw, read_iops, write_bw, write_iops, criteria)

class TestRampTimeReadWrite(object):
    ''' Test AMD64 NVM Ramp-up Time Read Write
        Performance of the AMD64 system
        Fixtures:
            target_perf:
            ramp_times:
            write_pattern:
            my_mdb:
    '''
    @pytest.mark.skip(reason="Discerned for now")
    @pytest.mark.flaky(reruns=3, reruns_delay=60)
    @pytest.mark.parametrize('ramp_times', list(range(120, 181, 10)))
    @pytest.mark.parametrize('write_pattern', [0, 100])
    def test_run_io_operation(self, target_perf, write_pattern, ramp_times,
        my_mdb):
        read_bw, read_iops, write_bw, write_iops = target_perf.run_io_operation(
            1, '4k', '4k', write_pattern, ramp_times)

        log_io_metrics(read_bw, read_iops, write_bw, write_iops, 'ramp_')

        result = my_mdb.aggregate_ramp_metrics(write_pattern,
            ramp_times)
        logger.debug(f'write_pattern = {write_pattern}')
        logger.debug(f'ramp_times = {ramp_times}')
        logger.debug(f'result = {result}')

