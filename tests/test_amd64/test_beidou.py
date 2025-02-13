# Contents of tests/test_amd64/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
import logging
# import pytest
# from system.amd64 import PlatformFactory

# Set up logger
logger = logging.getLogger(__name__)


class TestBeidou:
    '''Duplicate of Beidou configuration'''
    def test_get_system_info(self, amd64):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64: The system instance being tested.
            amd64 (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s', amd64.vendor)
        logger.info('Model = %s', amd64.model)
        logger.info('Name = %s', amd64.name)
        logger.info('Total Memory Size = %s GB', amd64.memory_size)
        assert amd64.vendor == amd64.api.system.manufacturer
        assert amd64.model == amd64.api.system.model
        assert amd64.name == amd64.api.system.name
        assert (str(amd64.memory_size) + ' GB' ==
                amd64.api.system.memory)

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
        logger.info("hyperthreading = %s", amd64.cpu.hyperthreading)
        assert (amd64.cpu.hyperthreading ==
                amd64.api.cpu.hyperthreading)
        assert amd64.cpu.cores == amd64.api.cpu.cores
        assert amd64.cpu.model == amd64.api.cpu.model_name

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
        assert amd64.system.model == amd64.api.system.model
        assert amd64.system.name == amd64.api.system.name
        assert (str(amd64.system.memory) ==
                amd64.api.system.memory)
