import logging
# from dataclasses import asdict
# Set up logger
logger = logging.getLogger(__name__)


class TestRaspberryPi:
    def test_get_memory_size(self, drone):
        value, unit = drone._get_memory_size()
        logger.info("memory_size = %s %s", value, unit)

    # def test_get_cpu_info(self, drone):
    def test_cpu(self, drone):
        # cpu_info = drone.get_cpu_info()
        # logger.info("vendor = %s", cpu_info.vendor)
        # logger.info("model = %s", cpu_info.model)
        # logger.info("hyperthreading = %s", cpu_info.hyperthreading)
        # logger.info("cores = %s", cpu_info.cores)
        cpu_spec = drone.api.cpu
        logger.debug("cpu_spec = %s", cpu_spec)
        cpu_info = drone.cpu
        logger.info("vendor = %s", cpu_info.vendor)
        logger.info("model = %s", cpu_info.model)
        logger.info("hyperthreading = %s", cpu_info.hyperthreading)
        logger.info("cores = %s", cpu_info.cores)
        # assert asdict(cpu_spec) == asdict(cpu_info)

    def test_system(self, drone):
        system_info = drone.system
        logger.info("manufacturer = %s", system_info.manufacturer)
        logger.info("model = %s", system_info.model)
        logger.info("name = %s", system_info.name)
        logger.info("rev = %s", system_info.rev)
        logger.info("memory = %s", system_info.memory)
