# Contents of tests/test_amd64/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
import logging
# import pytest
# from system.amd64 import PlatformFactory

# Set up logger
logger = logging.getLogger(__name__)


class TestBeidou:
    '''Duplicate of Beidou configuration'''
    def test_get_cpu_info(self, amd64_system):
        """Test for verifying hyperthreading setting.

        Args:
            beidou: The system instance being tested.
        """
        logger.info("CPU(s) = %s", amd64_system.cpu_num)
        logger.info("CPU model = %s", amd64_system.cpu_name)
        logger.info("hyperthreading = %s", amd64_system.cpu.hyperthreading)
        assert (amd64_system.cpu.hyperthreading ==
                amd64_system.api.cpu.hyperthreading)
        assert amd64_system.cpu_num == amd64_system.api.cpu.cores
        assert amd64_system.cpu_name == amd64_system.api.cpu.model_name

    def test_get_system_info(self, amd64_system):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64_system: The system instance being tested.
            amd64_system (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s', amd64_system.vendor)
        logger.info('Model = %s', amd64_system.model)
        logger.info('Name = %s', amd64_system.name)
        logger.info('Total Memory Size = %s GB', amd64_system.memory_size)
        assert amd64_system.vendor == amd64_system.api.system.manufacturer
        assert amd64_system.model == amd64_system.api.system.model
        assert amd64_system.name == amd64_system.api.system.name
        assert (str(amd64_system.memory_size) + ' GB' ==
                amd64_system.api.system.memory)

    def test_mac_address(self, amd64_system):
        """Test for verifying MAC address of the system.

        Args:
            amd64_system: The system instance being tested.
            amd64_system (dict): Expected configuration data for validation.
        """
        logger.info("MAC Address = %s", amd64_system.mac_address)
        assert amd64_system.mac_address == amd64_system.api.network.mac_address

    def test_cpu(self, amd64_system):
        '''docstring'''
        logger.info("Manufacturer = %s", amd64_system.cpu.vendor)
        logger.info("CPU(s) = %s", amd64_system.cpu.cores)
        logger.info("CPU model = %s", amd64_system.cpu.model)
        logger.info("hyperthreading = %s", amd64_system.cpu.hyperthreading)
        assert (amd64_system.cpu.hyperthreading ==
                amd64_system.api.cpu.hyperthreading)
        assert amd64_system.cpu.cores == amd64_system.api.cpu.cores
        assert amd64_system.cpu.model == amd64_system.api.cpu.model_name
