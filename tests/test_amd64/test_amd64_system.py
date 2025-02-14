# Contents of tests/test_amd64/test_amd64_system.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def amd64_settings():
    """Fixture to load AMD64 settings from a JSON file."""
    with open('config/amd64_nvme.json', 'r', encoding='utf-8') as f:
        return json.load(f)


class TestAMD64System1:
    '''Duplicate of TestAMD64NVMe'''
    def test_get_logic_processors(self, amd64, amd64_settings):
        """Test for verifying hyperthreading setting.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info("hyperthreading = %s", amd64.cpu.hyperthreading)
        assert (amd64.cpu.hyperthreading ==
                amd64_settings['CPU Information']['Hyperthreading'])

    def test_memory_size(self, amd64):
        """Test for verifying memory size of the system.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        memory_size = amd64.memory_size
        logger.info("Memory Size = %s GB", memory_size)

    def test_mac_address(self, amd64):
        """Test for verifying MAC address of the system.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        mac_address = amd64.mac_address
        logger.info("MAC Address = %s", mac_address)

    def test_get_system_info(self, amd64, amd64_settings):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    amd64.vendor,
                    amd64.model,
                    amd64.name)
        assert (amd64.vendor ==
                amd64_settings['System Information']["Manufacturer"])
        assert (amd64.model ==
                amd64_settings['System Information']["Model"])


class TestAMD64System:
    '''docstring'''
    def test_get_system_info(self, amd64):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64: The system instance being tested.
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
