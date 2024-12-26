# Contents of amd64_ping.py
'''Copyright (c) 2024 Jaron Cheng'''

from unit.ping import LinuxPing


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
