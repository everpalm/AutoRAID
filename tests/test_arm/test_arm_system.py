import logging

# Set up logger
logger = logging.getLogger(__name__)


class TestRaspberryPi:
    def test_get_memory_size(self, drone):
        value, unit = drone._get_memory_size()
        logger.info("memory_size = %s %s", value, unit)

    def test_get_cpu_info(self, drone):
        cpu_info = drone.get_cpu_info()
        logger.info("vendor_name = %s", cpu_info.vendor_name)
        logger.info("model_name = %s", cpu_info.model_name)
        logger.info("hyperthreading = %s", cpu_info.hyperthreading)

    def test_get_system_info(self, drone):
        system_info = drone.get_system_info()
        logger.info("manufacturer = %s", system_info.manufacturer)
        logger.info("model = %s", system_info.model)
        logger.info("name = %s", system_info.name)
        logger.info("rev = %s", system_info.rev)
