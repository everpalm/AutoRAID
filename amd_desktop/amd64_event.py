from abc import ABC
from abc import abstractmethod
import logging
import re

logger = logging.getLogger(__name__)


class WinEvent(ABC):
    @abstractmethod
    def find_error_event(self):
        pass

class AMD64Event(WinEvent):
    def __init__(self, platform, config_file):
        self.config_file = config_file
        self._platform = platform 
        self._api = platform.api
        self.error_features = []

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, file_name):
        self._config_file = f'config/{file_name}'
        print(f'self._config_file = {self._config_file}')
        # self._config_file = 'test'

    def find_error_event(self, log_name, event_id, pattern):
        try:
            # pattern = r'Disk (\d+) has been surprise removed.'
            output = self._api.command_line._original(self._api,
                # 'powershell "Get-EventLog -LogName System|Where-Object'
                # ' { $_.EventID -eq 157 }"')
                f'powershell "Get-EventLog -LogName {log_name}|Where-Object'
                f' {{ $_.EventID -eq {event_id} }}"')
            logger.debug(f'output = {output}')
            if output:
                for line in output:
                    # logger.debug(f'line = {line}')
                    if line:
                        match = re.search(pattern, line)
                        if match:
                            self.error_features.append(int(match.group(1)))
                            logger.debug(f"self.error_features = {self.error_features}")
                return True
            else:
                return False          
        except Exception as e:
            logger.error(f'find_error_event: {e}')

        
