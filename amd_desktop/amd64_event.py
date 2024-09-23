from collections import defaultdict
from abc import ABC
from abc import abstractmethod
import logging
import re

logger = logging.getLogger(__name__)


class SystemLogging(ABC):
    @abstractmethod
    def find_error(self):
        pass

class WindowsEvent(SystemLogging):
    def __init__(self, platform, config_file):
        self.config_file = config_file
        self._platform = platform 
        self._api = platform.api
        self.error_features = defaultdict(list)

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, file_name):
        self._config_file = f'config/{file_name}'
        logger.debug(f'self._config_file = {self._config_file}')

    def find_error(self, log_name, event_id, pattern):
        try:
            output = self._api.command_line._original(self._api,
                f'powershell "Get-EventLog -LogName {log_name}|Where-Object'
                f' {{ $_.EventID -eq {event_id} }}"')
            logger.debug(f'output = {output}')
            if output:
                for line in output:
                    if line:
                        print(f'line = {line}')
                        match = re.search(pattern, line)
                        if match:
                            value = str(match.group(1))
                            if event_id not in self.error_features:
                                self.error_features[event_id] = [value]
                            else:
                                if value not in self.error_features[event_id]:
                                    self.error_features[event_id].append(value)
                logger.debug(f"self.error_features = {self.error_features}")
                return True
            else:
                return False          
        except Exception as e:
            logger.error(f'find_error_event: {e}')

        
