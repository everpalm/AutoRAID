# Contents of tests/test_amd64/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
import logging
from dataclasses import asdict

# import pytest
# from system.amd64 import PlatformFactory

# Set up logger
logger = logging.getLogger(__name__)


class TestBeidou:
    '''Duplicate of Beidou configuration'''
    def test_mac_address(self, amd64):
        """Test for verifying MAC address of the system.

        Args:
            amd64: The system instance being tested.
            amd64 (dict): Expected configuration data for validation.
        """
        logger.info("MAC Address = %s", amd64.mac_address)
        assert amd64.mac_address == amd64.api.network.mac_address

    def test_cpu(self, amd64):
        '''docstring'''
        logger.info("Manufacturer = %s", amd64.cpu.vendor)
        logger.info("CPU(s) = %s", amd64.cpu.cores)
        logger.info("CPU model = %s", amd64.cpu.model)
        logger.info("Hyperthreading = %s", amd64.cpu.hyperthreading)
        assert asdict(amd64.cpu) == asdict(amd64.api.cpu)

    def test_system(self, amd64):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64: The system instance being tested.
            amd64 (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s', amd64.system.manufacturer)
        logger.info('Model = %s', amd64.system.model)
        logger.info('Name = %s', amd64.system.name)
        logger.info('Rev = %s', amd64.system.rev)
        logger.info('Total Memory Size = %s ', amd64.system.memory)
        assert amd64.system.manufacturer == (
            amd64.api.system.manufacturer
        )

        assert asdict(amd64.system) == asdict(amd64.api.system)
