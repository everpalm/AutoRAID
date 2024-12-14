'''Copyright (c) 2024 Jaron Cheng'''
# from collections import defaultdict
import logging
import re
from abc import ABC
from abc import abstractmethod
from amd_desktop.amd64_nvme import AMD64NVMe

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

# 抽象基類，定義通用的日誌處理器接口
class SystemLogging(ABC):
    """
    Abstract Base Class: System Logging Manager

    This abstract base class defines a standard interface for system log management, 
    specifically for finding and clearing system error logs.
    Concrete implementations inheriting from this class should provide 
    platform-specific log handling logic.

    Abstract Methods:
    - find_error(): Search and return system error logs
    - clear_error(): Clear system error logs

    Usage Example:
    ```python
    class WindowsSystemLogging(SystemLogging):
        def find_error(self):
            # Windows-specific error log finding logic
            pass

        def clear_error(self):
            # Windows-specific error log clearing logic
            pass
    ```

    Notes:
    - Subclasses must implement both abstract methods
    - Method implementations depend on specific operating systems or logging systems
    """
    @abstractmethod
    def find_error(self):
        """
        Find error logs in the system

        This method should:
        - Search system logs
        - Filter and return error-type logs
        - Potentially return a list, dictionary, or other appropriate data structure of error logs

        Returns:
            list or dict: Collection of system error logs
            None: If no error logs are found

        Raises:
            NotImplementedError: If the method is not implemented by a subclass
            PermissionError: If insufficient permissions to access logs
        """
        ...

    @abstractmethod
    def clear_error(self):
        """
        Clear error logs from the system

        This method should:
        - Delete or reset system error logs
        - Ensure deletion is safe and controlled
        - May require administrative privileges

        Returns:
            bool: Whether the log clearing operation was successful

        Raises:
            PermissionError: If insufficient privileges to clear logs
            NotImplementedError: If the method is not implemented by a subclass
        """
        ...


# Windows 平台的日誌處理器
class WindowsEvent(SystemLogging):
    """
    Windows Event Log Management Class

    This class provides functionality to find and clear Windows system event logs
    by leveraging PowerShell commands through a platform-specific API.

    Attributes:
        _api (object): Platform-specific API for executing commands
        _error_features (dict): Dictionary to store discovered error features

    Args:
        platform (AMD64NVMe): Platform object containing API and error feature configurations

    Example:
        ```python
        platform = AMD64NVMe()
        windows_event = WindowsEvent(platform)
        
        # Find specific system events
        found = windows_event.find_error('System', 7, r'Error Pattern')
        
        # Clear system event log
        windows_event.clear_error()
        ```
    """
    def __init__(self, platform: AMD64NVMe):
        """
        Initialize WindowsEvent with platform-specific configurations.

        Args:
            platform (AMD64NVMe): Platform configuration object
        """
        self._api = platform.api
        self._error_features = platform.error_features

    def find_error(self, log_name, event_id, pattern):
        """
        Find and extract specific error events from Windows event logs.

        This method:
        - Uses PowerShell to query event logs
        - Filters events by log name and event ID
        - Searches for a specific regex pattern in event log entries
        - Stores matched values in _error_features

        Args:
            log_name (str): Name of the event log to search (e.g., 'System', 'Application')
            event_id (int): Specific event ID to filter
            pattern (str): Regex pattern to match within event log entries

        Returns:
            bool: True if matching events are found, False otherwise

        Raises:
            Exception: If there are issues executing the PowerShell command
        """
        try:
            output = self._api.command_line._original(self._api,
                f'powershell "Get-EventLog -LogName {log_name} | Where-Object'
                f' {{ $_.EventID -eq {event_id} }}"'
            )
            logger.debug("output = %s", output)

            match_found = False  # 追蹤是否有匹配的模式

            # 確保 event_id 在 _error_features 中存在
            if event_id not in self._error_features:
                self._error_features[event_id] = set()

            if output:
                for line in output:
                    if line:
                        logger.debug("line = %s", line)
                        match = re.search(pattern, line)
                        if match:
                            match_found = True  # 匹配成功
                            value = str(match.group(1))
                            self._error_features[event_id].add(value)

                logger.debug("self._error_features = %s", self._error_features)

            return match_found  # 根據是否有匹配模式來返回

        except re.error as e:  # 捕捉正則表達式錯誤
            logger.error("Invalid regex pattern %s", e)
            return False
        except Exception as e:
            logger.error("An unexpected error: %s", e)
            return False

    def clear_error(self):
        try:
            result = self._api.command_line._original(self._api,
                'powershell "Clear-EventLog -LogName system"'
            )
            logger.debug("result = %s", result)
            return True
        except Exception as e:
            logger.error("Error clearing system event log: %s", e)
            return False
