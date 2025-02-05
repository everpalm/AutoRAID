# Contents of tests/test_device/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
# import json
import logging
# import pytest
# Set up logger

logger = logging.getLogger(__name__)


class TestChunghua:
    '''docstring'''
    def test_controller_info(self, boot_device, network_api):
        '''fixture'''
        controller_info = boot_device.controller_info
        mapping_table = network_api.nvme_controller
        logger.debug("bus_device_func = %s", controller_info.bus_device_func)
        logger.debug("device = %s", controller_info.device)
        logger.debug("slot_id = %s", controller_info.slot_id)
        logger.debug("vid = %s", controller_info.vid)
        logger.debug("svid = %s", controller_info.svid)
        logger.debug("did = %s", controller_info.did)
        logger.debug("sdid = %s", controller_info.sdid)
        logger.debug("revision_id = %s", controller_info.revision_id)
        logger.debug("port_count = %s", controller_info.port_count)
        logger.debug("max_pd_of_per_vd = %s", controller_info.max_pd_of_per_vd)
        logger.debug("max_vd = %s", controller_info.max_vd)
        logger.debug("max_pd = %s", controller_info.max_pd)
        logger.debug("max_ns_of_per_vd = %s", controller_info.max_ns_of_per_vd)
        logger.debug("max_ns = %s", controller_info.max_ns)
        logger.debug("supported_raid_mode = %s",
                     controller_info.supported_raid_mode)
        logger.debug("cache = %s", controller_info.cache)
        logger.debug("supported_bga_features = %s",
                     controller_info.supported_bga_features)
        logger.debug("support_stripe_size = %s",
                     controller_info.support_stripe_size)
        logger.debug("supported_features = %s",
                     controller_info.supported_features)
        logger.debug("root_complexes = %s", controller_info.root_complexes)
        logger.debug("end_points = %s", controller_info.end_points)

        assert controller_info.bus_device_func == mapping_table.bus_device_func
        assert controller_info.device == mapping_table.device
        assert controller_info.slot_id == mapping_table.slot_id
        assert controller_info.vid == mapping_table.vid
        assert controller_info.svid == mapping_table.svid
        assert controller_info.did == mapping_table.did
        assert controller_info.sdid == mapping_table.sdid
        assert controller_info.revision_id == mapping_table.revision_id
        assert controller_info.port_count == mapping_table.port_count
        assert controller_info.max_pd_of_per_vd == \
            mapping_table.max_pd_of_per_vd
        assert controller_info.max_vd == mapping_table.max_vd
        assert controller_info.max_pd == mapping_table.max_pd
        assert controller_info.max_ns_of_per_vd == \
            mapping_table.max_ns_of_per_vd
        assert controller_info.max_ns == mapping_table.max_ns
        assert controller_info.supported_raid_mode == \
            mapping_table.supported_raid_mode
        assert controller_info.cache == mapping_table.cache
        assert controller_info.supported_bga_features == \
            mapping_table.supported_bga_features
        assert controller_info.support_stripe_size == \
            mapping_table.support_stripe_size
        assert controller_info.supported_features == \
            mapping_table.supported_features
        assert controller_info.root_complexes == mapping_table.root_complexes
        assert controller_info.end_points == mapping_table.end_points

    def test_virtual_drive_info(self, boot_device, network_api):
        '''fixture'''
        virtual_drive_info = boot_device.virtual_drive_info
        # mapping_table = network_api.nvme_controller
        logger.debug("vd_id = %s", virtual_drive_info.vd_id)
        logger.debug("name = %s", virtual_drive_info.name)
        logger.debug("status = %s", virtual_drive_info.status)
        logger.debug("importable = %s", virtual_drive_info.importable)
        logger.debug("raid_mode = %s", virtual_drive_info.raid_mode)
        logger.debug("size = %s", virtual_drive_info.size)
        logger.debug("pd_count = %s", virtual_drive_info.pd_count)
        logger.debug("pds = %s", virtual_drive_info.pds)
        logger.debug("stripe_block_size = %s", virtual_drive_info.stripe_block_size)
        logger.debug("sector_size = %s", virtual_drive_info.sector_size)
        logger.debug("total_of_vd = %s", virtual_drive_info.total_of_vd)
