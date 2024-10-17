from collections import defaultdict
from abc import ABC, abstractmethod
import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# 抽象基類，定義通用的日誌處理器接口
class SystemLogging(ABC):
    @abstractmethod
    def find_error(self):
        pass

    @abstractmethod
    def clear_error(self):
        pass

# Windows 平台的配置類
class WindowsEventConfig:
    def __init__(self, platform, config_file):
        self.config_file = config_file
        self._platform = platform
        self._api = platform.api
        self.error_features = defaultdict(set)

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, file_name):
        self._config_file = f'{file_name}'
        logger.debug(f'self._config_file = {self._config_file}')


# Windows 平台的日誌處理器
class WindowsEvent(SystemLogging):
    def __init__(self, config: WindowsEventConfig):
        self.config = config

    def find_error(self, log_name, event_id, pattern):
        try:
            output = self.config._api.command_line._original(
                self.config._api,
                f'powershell "Get-EventLog -LogName {log_name} | Where-Object'
                f' {{ $_.EventID -eq {event_id} }}"'
            )
            logger.debug(f'output = {output}')
            if output:
                for line in output:
                    if line:
                        logger.debug(f'line = {line}')
                        match = re.search(pattern, line)
                        if match:
                            value = str(match.group(1))
                            self.config.error_features[event_id].add(value)
                logger.debug(f"self.config.error_features = {self.config.error_features}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'find_error_event: {e}')
            return False

    def clear_error(self):
        try:
            result = self.config._api.command_line._original(
                self.config._api, 'powershell "Clear-EventLog -LogName system"'
            )
            logger.debug(f'result = {result}')
            return True
        except Exception as e:
            logger.error(f"Error clearing system event log: {e}")
            return False

# Linux 平台的配置類
class LinuxEventConfig:
    def __init__(self, platform, config_file):
        self.config_file = config_file
        self._platform = platform
        self._api = platform.api
        self.error_features = defaultdict(set)

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, file_name):
        self._config_file = f'{file_name}'
        logger.debug(f'self._config_file = {self._config_file}')

# Linux 平台的日誌處理器
class LinuxEvent(SystemLogging):
    def __init__(self, config: LinuxEventConfig):
        self.config = config

    def find_error(self, log_name, event_id, pattern):
        try:
            output = self.config._api.command_line._original(
                self.config._api,
                f'journalctl -u {log_name} | grep {event_id}'
            )
            logger.debug(f'output = {output}')
            if output:
                for line in output:
                    if line:
                        logger.debug(f'line = {line}')
                        match = re.search(pattern, line)
                        if match:
                            value = str(match.group(1))
                            self.config.error_features[event_id].add(value)
                logger.debug(f"self.config.error_features = {self.config.error_features}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'find_error_event: {e}')
            return False

    def clear_error(self):
        try:
            result = self.config._api.command_line._original(
                self.config._api, 'journalctl --vacuum-time=1s'
            )
            logger.debug(f'result = {result}')
            return True
        except Exception as e:
            logger.error(f"Error clearing Linux system event log: {e}")
            return False

# 工廠模式，根據平台動態創建日誌處理器
class LoggingFactory:
    @staticmethod
    def create_logging(platform, config_file):
        if platform == "windows":
            config = WindowsEventConfig(platform, config_file)
            return WindowsEvent(config)
        elif platform == "linux":
            config = LinuxEventConfig(platform, config_file)
            return LinuxEvent(config)
        else:
            raise ValueError(f"Unknown platform: {platform}")
