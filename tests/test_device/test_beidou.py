# Contents of tests/test_device/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
# import json
import logging
# import pytest
# Set up logger

logger = logging.getLogger(__name__)


class TestChunghua:
    '''docstring'''
    def test_get_controller_info(self, boot_device, network_api):
        '''fixture'''
        controller_info = boot_device.controller_info
        logger.info("bus_device_func = %s", controller_info.bus_device_func)
        logger.info("device = %s", controller_info.device)
        logger.info("slot_id = %s", controller_info.slot_id)
        logger.info("vid = %s", controller_info.vid)
        logger.info("svid = %s", controller_info.svid)
        logger.info("did = %s", controller_info.did)
        logger.info("sdid = %s", controller_info.sdid)
        logger.info("revision_id = %s", controller_info.revision_id)
        logger.info("port_count = %s", controller_info.port_count)
        logger.info("max_pd_of_per_vd = %s", controller_info.max_pd_of_per_vd)
        logger.info("max_vd = %s", controller_info.max_vd)
        logger.info("max_pd = %s", controller_info.max_pd)
        logger.info("max_ns_of_per_vd = %s", controller_info.max_ns_of_per_vd)
        logger.info("max_ns = %s", controller_info.max_ns)
        logger.info("supported_raid_mode = %s",
                    controller_info.supported_raid_mode)
        logger.info("cache = %s", controller_info.cache)
        logger.info("supported_bga_features = %s",
                    controller_info.supported_bga_features)
        logger.info("support_stripe_size = %s",
                    controller_info.support_stripe_size)
        logger.info("supported_features = %s",
                    controller_info.supported_features)
        logger.info("root_complexes = %s", controller_info.root_complexes)
        logger.info("end_points = %s", controller_info.end_points)
        logger.info("nvme_controller = %s", network_api.nvme_controller)
