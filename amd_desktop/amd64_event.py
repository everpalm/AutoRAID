# from collections import defaultdict
from abc import ABC, abstractmethod
from amd_desktop.amd64_nvme import AMD64NVMe
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


class MatchFoundException(Exception):
    pass


# Windows 平台的日誌處理器
class WindowsEvent(SystemLogging):

    def __init__(self, platform: AMD64NVMe):
        self._api = platform.api
        self._error_features = platform.error_features

    def find_error(self, log_name, event_id, pattern):
        try:
            output = self._api.command_line._original(self._api,
                f'powershell "Get-EventLog -LogName {log_name} | Where-Object'
                f' {{ $_.EventID -eq {event_id} }}"'
            )
            logger.debug(f'output = {output}')
            
            match_found = False  # 追蹤是否有匹配的模式

            if output:
                for line in output:
                    if line:
                        logger.debug(f'line = {line}')
                        match = re.search(pattern, line)
                        if match:
                            match_found = True  # 匹配成功
                            value = str(match.group(1))
                            self._error_features[event_id].add(value)
                            raise MatchFoundException(f"Match found for event ID {event_id}: {value}")
                logger.debug(f"self._error_features = {self._error_features}")
                
            
            return match_found  # 根據是否有匹配模式來返回
        except MatchFoundException as e:
            logger.info(f"Process stopped due to: {e}")
            raise  # 如果需要在外部捕捉這個異常，可以選擇重新拋出

        except Exception as e:
            logger.error(f'find_error_event: {e}')
            return False

    def clear_error(self):
        try:
            result = self._api.command_line._original(self._api,
                'powershell "Clear-EventLog -LogName system"'
            )
            logger.debug(f'result = {result}')
            return True
        except Exception as e:
            logger.error(f"Error clearing system event log: {e}")
            return False
