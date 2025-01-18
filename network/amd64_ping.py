# Contents of network.amd64_ping.py
'''Copyright (c) 2024 Jaron Cheng'''
from abc import ABC
from abc import abstractmethod
from network.ping import PingBase
from network.ping import LinuxPing
from network.ping import WindowsPing


class AMD64Ping(LinuxPing):
    """A class to represent the AMD64 Ping functionality.

    This class inherits from the `LinuxPing` class and provides the same
    functionality tailored for AMD64-based systems. It can be used to
    perform network connectivity checks and measure network latency for
    systems running on the AMD64 architecture.

    Attributes:
        Inherits all attributes from the `LinuxPing` class.

    Methods:
        Inherits all methods from the `LinuxPing` class.
    """


class BasePingFactory(ABC):
    '''docstring'''
    @abstractmethod
    def initiate(self, os_type: str, **kwargs) -> PingBase:
        pass


class PingFactory(BasePingFactory):
    def initiate(self, os_type: str, **kwargs) -> PingBase:
        if os_type == 'Windows':
            return WindowsPing(**kwargs)
        elif os_type == 'Linux':
            return LinuxPing(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")
