# Contents of amd64_warmboot.py
from abc import ABC, abstractmethod
import logging
from amd_desktop.amd64_nvme import AMD64NVMe
from unit.log_handler import get_logger

# logger = logging.getLogger(__name__)
logger = get_logger(__name__, logging.INFO)

class WarmBoot(ABC):
    """Abstract base class for warm boot operations."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the warm boot process."""
        ...


class WindowsWarmBoot(WarmBoot):
    """Warm boot implementation for Windows systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Executing warm boot for Windows...")
        try:
            # Execute the warm boot command
            self._api.command_line._original(self._api, 'shutdown /r /t 0')
            logger.info("Warm boot executed successfully for Windows.")
            return True
        
        except Exception as e:
            logger.error(f"Error during Windows warm boot execution: {e}")
            return False


class LinuxWarmBoot(WarmBoot):
    """Warm boot implementation for Linux systems."""
    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api

    def execute(self) -> bool:
        logger.info("Executing warm boot for Linux...")
        try:
            # Execute the warm boot command
            self._api.command_line(self._api, 'sudo reboot')
            logger.info("Warm boot executed successfully for Linux.")
            return True
            
        except Exception as e:
            logger.error(f"Error during Linux warm boot execution: {e}")
            return False
