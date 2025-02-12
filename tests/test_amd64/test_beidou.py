# Contents of tests/test_amd6/test_beidou.py
'''Copyright (c) 2025 Jaron Cheng'''
import logging
import pytest
from system.amd64 import PlatformFactory

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def beidou(network_api):
    """
    docstring
    """
    print("\n\033[32m================== Setup Beidou ================\033[0m")
    factory = PlatformFactory(network_api)
    return factory.create_platform(interface=network_api)


class TestBeidou:
    '''Duplicate of Beidou configuration'''
    def test_get_cpu_info(self, beidou):
        """Test for verifying hyperthreading setting.

        Args:
            beidou: The system instance being tested.
        """
        logger.info("CPU(s) = %s", beidou.cpu_num)
        logger.info("CPU model = %s", beidou.cpu_name)
        logger.info("hyperthreading = %s", beidou.hyperthreading)
        assert (beidou.hyperthreading ==
                beidou.api.cpu.hyperthreading)
        assert beidou.cpu_num == beidou.api.cpu.cores
        assert beidou.cpu_name == beidou.api.cpu.model_name

    def test_get_system_info(self, beidou):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            beidou: The system instance being tested.
            beidou (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s', beidou.vendor)
        logger.info('Model = %s', beidou.model)
        logger.info('Name = %s', beidou.name)
        logger.info('Total Memory Size = %s GB', beidou.memory_size)
        assert beidou.vendor == beidou.api.system.manufacturer
        assert beidou.model == beidou.api.system.model
        assert beidou.name == beidou.api.system.name
        assert str(beidou.memory_size) + ' GB' == beidou.api.system.memory

    # def test_memory_size(self, beidou):
    #     """Test for verifying memory size of the system.

    #     Args:
    #         beidou: The system instance being tested.
    #         beidou (dict): Expected configuration data for validation.
    #     """
    #     memory_size = beidou.memory_size
    #     logger.info("Memory Size = %s GB", memory_size)

    def test_mac_address(self, beidou):
        """Test for verifying MAC address of the system.

        Args:
            beidou: The system instance being tested.
            beidou (dict): Expected configuration data for validation.
        """
        mac_address = beidou.mac_address
        logger.info("MAC Address = %s", mac_address)
