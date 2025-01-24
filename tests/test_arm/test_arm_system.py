import logging

# Set up logger
logger = logging.getLogger(__name__)


class TestRaspberryPi:
    def test_get_memory_size(self, drone):
        value, unit = drone._get_memory_size()
        logger.info("memory_size = %s %s", value, unit)

    def test_get_cpu_info(self, drone):
        model_name = drone.get_cpu_info()
        logger.info("model_name = %s", model_name)
