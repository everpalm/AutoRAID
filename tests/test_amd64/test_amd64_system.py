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


@pytest.mark.skip(reason="Depricated")
class TestAMD64System:
    '''Duplicate of TestAMD64NVMe'''
    def test_get_hyperthreading(self, amd64_system, amd64_settings):
        """Test for verifying hyperthreading setting.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info("hyperthreading = %s", amd64_system.hyperthreading)
        assert (amd64_system.hyperthreading ==
                amd64_settings['CPU Information']['Hyperthreading'])

    def test_memory_size(self, amd64_system):
        """Test for verifying memory size of the system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        memory_size = amd64_system.memory_size
        logger.info("Memory Size = %s GB", memory_size)

    def test_mac_address(self, amd64_system):
        """Test for verifying MAC address of the system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        mac_address = amd64_system.mac_address
        logger.info("MAC Address = %s", mac_address)

    def test_get_cpu_info(self, amd64_system, amd64_settings):
        """Test for verifying CPU model and core count.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('CPU(s) = %s, CPU model = %s', amd64_system.cpu_num,
                    amd64_system.cpu_name)
        assert (amd64_system.cpu_num ==
                amd64_settings['CPU Information']["CPU(s)"])
        assert (amd64_system.cpu_name ==
                amd64_settings['CPU Information']["Model Name"])

    def test_get_system_info(self, amd64_system, amd64_settings):
        """Test for verifying system manufacturer, model, and operating system.

        Args:
            amd64_system: The system instance being tested.
            AMD64_SETTINGS (dict): Expected configuration data for validation.
        """
        logger.info('Manufacturer = %s, Model = %s, Name = %s',
                    amd64_system.vendor,
                    amd64_system.model,
                    amd64_system.name)
        assert (amd64_system.vendor ==
                amd64_settings['System Information']["Manufacturer"])
        assert (amd64_system.model ==
                amd64_settings['System Information']["Model"])
