# Contents of tests/test_device/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
import json
import logging
import pytest
from tests.test_storage.test_stress import (
    TestOneShotReadWriteStress as Stress)
from tests.test_commandline.test_mnv_cli_rebuild import (
    TestCLIResetPD1 as ResetPD1)
from tests.test_commandline.test_mnv_cli_rebuild import (
    TestCLIRebuildPD1 as RebuildPD1)
from unit.json_handler import load_and_sort_json

# Set up logger
logger = logging.getLogger(__name__)

# 定義配置檔案與對應鍵
CONFIG_FILES = {
    "reset_pd1": ("config/test_mnv_cli_reset_pd1.json", "ID"),
    "rebuild_pd1": ("config/test_mnv_cli_rebuild_pd1_changlong.json", "ID")
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


@pytest.mark.order(1)
class TestFunctionalChanglong:
    '''docstring'''
    def test_controller_info(self, boot_device, network_api):
        '''fixture'''
        from_controller = boot_device.controller_info
        from_table = network_api.nvme_controller
        logger.debug("bus_device_func = %s", from_controller.bus_device_func)
        logger.debug("device = %s", from_controller.device)
        logger.debug("slot_id = %s", from_controller.slot_id)
        logger.debug("vid = %s", from_controller.vid)
        logger.debug("svid = %s", from_controller.svid)
        logger.debug("did = %s", from_controller.did)
        logger.debug("sdid = %s", from_controller.sdid)
        logger.debug("revision_id = %s", from_controller.revision_id)
        logger.debug("port_count = %s", from_controller.port_count)
        logger.debug("max_pd_of_per_vd = %s", from_controller.max_pd_of_per_vd)
        logger.debug("max_vd = %s", from_controller.max_vd)
        logger.debug("max_pd = %s", from_controller.max_pd)
        logger.debug("max_ns_of_per_vd = %s", from_controller.max_ns_of_per_vd)
        logger.debug("max_ns = %s", from_controller.max_ns)
        logger.debug("supported_raid_mode = %s",
                     from_controller.supported_raid_mode)
        logger.debug("cache = %s", from_controller.cache)
        logger.debug("supported_bga_features = %s",
                     from_controller.supported_bga_features)
        logger.debug("support_stripe_size = %s",
                     from_controller.support_stripe_size)
        logger.debug("supported_features = %s",
                     from_controller.supported_features)
        logger.debug("root_complexes = %s", from_controller.root_complexes)
        logger.debug("end_points = %s", from_controller.end_points)

        assert from_controller.bus_device_func == from_table.bus_device_func
        assert from_controller.device == from_table.device
        assert from_controller.slot_id == from_table.slot_id
        assert from_controller.vid == from_table.vid
        assert from_controller.svid == from_table.svid
        assert from_controller.did == from_table.did
        assert from_controller.sdid == from_table.sdid
        assert from_controller.revision_id == from_table.revision_id
        assert from_controller.port_count == from_table.port_count
        assert from_controller.max_pd_of_per_vd == \
            from_table.max_pd_of_per_vd
        assert from_controller.max_vd == from_table.max_vd
        assert from_controller.max_pd == from_table.max_pd
        assert from_controller.max_ns_of_per_vd == \
            from_table.max_ns_of_per_vd
        assert from_controller.max_ns == from_table.max_ns
        assert from_controller.supported_raid_mode == \
            from_table.supported_raid_mode
        assert from_controller.cache == from_table.cache
        assert from_controller.supported_bga_features == \
            from_table.supported_bga_features
        assert from_controller.support_stripe_size == \
            from_table.support_stripe_size
        assert from_controller.supported_features == \
            from_table.supported_features
        assert from_controller.root_complexes == from_table.root_complexes
        assert from_controller.end_points == from_table.end_points

    def test_virtual_drive_info(self, boot_device, network_api):
        '''fixture'''
        from_controller = boot_device.virtual_drive_info
        from_table = network_api.virtual_drive
        logger.debug("virtual_drive = %s", from_controller)
        logger.debug("from_table = %s", from_table)

        assert from_controller == from_table


@pytest.mark.order(2)
class TestResetChanglongPD1(ResetPD1):
    """
    Test suite for verifying Windows Warm Boot functionality with network
    """
    # @pytest.mark.parametrize('test_case', SORTED_DATA["reset_pd1"])
    # def test_commandline(self, mnv_cli, test_case):
    #     '''docstring'''
    #     reset_pd1_result = mnv_cli.interpret(test_case["Command"])
    #     logger.debug('reset_pd1_result = %s', reset_pd1_result)
    #     assert reset_pd1_result == test_case["Expected"]


@pytest.mark.order(3)
class TestStressAfterResetChanglongPD1(Stress):
    '''Test One-shot stress after reset PD1 of Changlong card'''


@pytest.mark.order(4)
class TestRebuildChanglongPD1(RebuildPD1):
    """
    Test rebuilding backend PD1 of Changlong card
    """
    # @pytest.mark.parametrize('test_case', SORTED_DATA["rebuild_pd1"])
    # def test_commandline(self, mnv_cli, test_case):
    #     '''docstring'''
    #     rebuild_pd1_result = mnv_cli.interpret(test_case["Command"])
    #     logger.debug('rebuild_pd1_result = %s', rebuild_pd1_result)
    #     assert rebuild_pd1_result == test_case["Expected"]


@pytest.mark.order(5)
@pytest.mark.flaky(reruns=330, reruns_delay=60)
class TestRebuildChanglongPD1Complete:
    '''Resemble functional Changlong'''
    def test_virtual_drive_info(self, boot_device):
        '''fixture'''
        from_controller = boot_device.virtual_drive_info

        # 檢查是否仍在 rebuilding
        rebuilding = any(
            vd.bga_progress and "Rebuilding is running" in vd.bga_progress
            for vd in from_controller
        )

        # 顯示 rebuilding 進度
        if rebuilding:
            for vd in from_controller:
                if vd.bga_progress:
                    logger.debug("%s", vd.bga_progress)

            # 確保 rebuilding 已完成
        assert all(
            vd.status == "Functional" for vd in from_controller
        ), "Rebuilding did not complete successfully"
