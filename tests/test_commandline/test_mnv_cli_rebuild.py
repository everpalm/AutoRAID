# Contents of tests/test_commandline/test_mnv_cli_rebuild.py
'''Unit tests for commandline class, which includes testing the execution of
mnv_cli commands to verify rebuild commands and system responses

   Copyright (c) 2024 Jaron Cheng
'''
import json
import logging
import pytest
from tests.test_storage.test_partitioning import (
    TestDiskVolume as Partitioning)
from tests.test_storage.test_stress import (
    TestOneShotReadWriteStress as Stress)
from unit.json_handler import load_and_sort_json

# Set up logger
logger = logging.getLogger(__name__)

# Define configuration and key
CONFIG_FILES = {
    "bga_off": ("config/test_mnv_cli_bga_off.json", "ID"),
    "bga_on": ("config/test_mnv_cli_bga_on.json", "ID"),
    "bga_high": ("config/test_mnv_cli_bga_high.json", "ID"),
    "bga_low": ("config/test_mnv_cli_bga_low.json", "ID"),
    "bga_medium": ("config/test_mnv_cli_bga_medium.json", "ID"),
    "bga_invalid": ("config/test_mnv_cli_bga_invalid.json", "ID"),
    "reset_pd1": ("config/test_mnv_cli_reset_pd1.json", "ID"),
    "reset_pd2": ("config/test_mnv_cli_reset_pd2.json", "ID"),
    "rebuild_pd1": ("config/test_mnv_cli_rebuild_pd1.json", "ID"),
    "rebuild_pd2": ("config/test_mnv_cli_rebuild_pd2.json", "ID"),
    "rebuild_pd1_stop": ("config/test_mnv_cli_rebuild_pd1_stop.json", "ID"),
    "rebuild_pd2_stop": ("config/test_mnv_cli_rebuild_pd2_stop.json", "ID"),
    "mp_start": ("config/test_mnv_cli_mp_start.json", "ID"),
    "mp_stop": ("config/test_mnv_cli_mp_stop.json", "ID"),
    "vd_delete": ("config/test_mnv_cli_vd_delete.json", "ID"),
    "vd_create_r1": ("config/test_mnv_cli_vd_create_r1.json", "ID"),
    "rebuild_pd1_stop0": ("config/test_mnv_cli_rebuild_pd1_stop0.json", "ID"),
    "rebuild_pd2_stop0": ("config/test_mnv_cli_rebuild_pd2_stop0.json", "ID")
}

# Load and process file
SORTED_DATA = {
    name: load_and_sort_json(path, key) if key else json.load(open(
        path,
        'r',
        encoding='utf-8'
    ))
    for name, (path, key) in CONFIG_FILES.items()
}


class TestCLIBGAOff:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_off"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_off_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_off_result = %s', bga_off_result)
        assert bga_off_result == test_case["Expected"]


class TestCLIBGAOn:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_on"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_on_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_on_result = %s', bga_on_result)
        assert bga_on_result == test_case["Expected"]


class TestCLIBGAHigh:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_high"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_high_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_high_result = %s', bga_high_result)
        assert bga_high_result == test_case["Expected"]


class TestCLIBGALow:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_low"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_low_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_low_result = %s', bga_low_result)
        assert bga_low_result == test_case["Expected"]


class TestCLIBGAMedium:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_medium"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_medium_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_medium_result = %s', bga_medium_result)
        assert bga_medium_result == test_case["Expected"]


class TestCLIBGAInvalid:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["bga_invalid"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        bga_invalid_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('bga_invalid_result = %s', bga_invalid_result)
        assert bga_invalid_result == test_case["Expected"]


class TestCLIPartitioningBeforehand(Partitioning):
    '''docstring'''


@pytest.mark.flaky(reruns=4, reruns_delay=5)
class TestCLIResetPD1:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pd1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pd1_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pd1_result = %s', reset_pd1_result)
        assert reset_pd1_result == test_case["Expected"]


class TestCLIStressAfterResetPD1(Stress):
    '''docstring'''


class TestCLIRebuildPD1:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd1_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd1_result = %s', rebuild_pd1_result)
        assert rebuild_pd1_result == test_case["Expected"]


@pytest.mark.xfail
class TestCLIRebuildPD1Stop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1_stop0"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd1_stop0_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd1_stop0_result = %s', rebuild_pd1_stop0_result)
        assert rebuild_pd1_stop0_result == test_case["Expected"]


@pytest.mark.xfail
class TestCLIRebuildPD1StopAgain:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd1_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd1_stop_result = %s', rebuild_pd1_stop_result)
        assert rebuild_pd1_stop_result == test_case["Expected"]


@pytest.mark.flaky(reruns=2, reruns_delay=5)
class TestCLIVDDelete:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["vd_delete"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        vd_delete_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('vd_delete_result = %s', vd_delete_result)
        assert vd_delete_result == test_case["Expected"]


class TestCLIVDCreateR1:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["vd_create_r1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        vd_create_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('vd_create_result = %s', vd_create_result)
        assert vd_create_result == test_case["Expected"]


class TestCLIPartitioning(Partitioning):
    '''docstring'''


class TestCLIMPStart:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["mp_start"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        mp_start_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('mp_start_result = %s', mp_start_result)
        assert mp_start_result == test_case["Expected"]


class TestCLIMPStop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["mp_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        mp_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('mp_stop_result = %s', mp_stop_result)
        assert mp_stop_result == test_case["Expected"]


@pytest.mark.flaky(reruns=4, reruns_delay=5)
class TestCLIResetPD2:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pd2"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        reset_pd2_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('reset_pd2_result = %s', reset_pd2_result)
        assert reset_pd2_result == test_case["Expected"]


class TestCLIStressAfterResetPD2(Stress):
    '''docstring'''


class TestCLIRebuildPD2:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd2"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd2_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd2_result = %s', rebuild_pd2_result)
        assert rebuild_pd2_result == test_case["Expected"]


@pytest.mark.xfail
class TestCLIRebuildPD2Stop:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd2_stop0"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd2_stop0_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd2_stop0_result = %s', rebuild_pd2_stop0_result)
        assert rebuild_pd2_stop0_result == test_case["Expected"]


@pytest.mark.xfail
class TestCLIRebuildPD2StopAgain:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd2_stop"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        rebuild_pd2_stop_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('rebuild_pd2_stop_result = %s', rebuild_pd2_stop_result)
        assert rebuild_pd2_stop_result == test_case["Expected"]


@pytest.mark.flaky(reruns=2, reruns_delay=5)
class TestCLIVDDeleteAgain:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["vd_delete"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        vd_delete_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('vd_delete_result = %s', vd_delete_result)
        assert vd_delete_result == test_case["Expected"]


class TestCLIVDCreateR1Again:
    '''docstring'''
    @pytest.mark.parametrize('test_case', SORTED_DATA["vd_create_r1"])
    def test_commandline(self, mnv_cli, test_case):
        '''docstring'''
        vd_create_result = mnv_cli.interpret(test_case["Command"])
        logger.debug('vd_create_result = %s', vd_create_result)
        assert vd_create_result == test_case["Expected"]


class TestCLIPartitioningLast(Partitioning):
    '''docstring'''
