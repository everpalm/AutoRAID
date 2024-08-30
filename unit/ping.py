'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from abc import ABC
from abc import abstractmethod

logger = logging.getLogger(__name__)

class PingBase(ABC):
    """
    A base class for handling ping operations.

    This class defines the basic structure for sending and processing ping commands
    and parsing the results. It serves as an abstract base class that must be
    extended by specific implementations for different operating systems.

    Attributes:
        sent (int): The number of packets sent.
        received (int): The number of packets received.
        lost (int): The number of packets lost.
        minimum (float): The minimum round-trip time (RTT).
        maximum (float): The maximum round-trip time (RTT).
        average (float): The average round-trip time (RTT).
    """
    def __init__(self):
        """
        Initializes the PingBase class with default values for packet statistics.
        """
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0
        # self.deviation = 0

    @abstractmethod
    def ping(self, count=4):
        """
        Sends a ping request.

        This method should be implemented by subclasses to send ping requests
        and process the results.

        Args:
            count (int): The number of ping requests to send. Default is 4.
        """
        pass

    def _parse_packets(self, output, packet_regex):
        """
        Parses packet statistics from the ping command output.

        Args:
            output (str): The output of the ping command.
            packet_regex (str): The regular expression pattern to match packet statistics.

        Returns:
            bool: True if the packet statistics were successfully parsed, False otherwise.
        """
        match = re.search(packet_regex, output)
        if match:
            self.sent = int(match.group(1))
            self.received = int(match.group(2))
            self.lost = self.sent - self.received  # Calculate packet loss
            return True
        else:
            logger.warning(f"Packet statistics parsing failed: {output}")
        return False


class LinuxPing(PingBase):
    """
    A class for handling ping operations on Linux systems.

    This class extends PingBase to provide an implementation of ping operations
    specifically for Linux-based systems. It parses Linux-specific ping command
    outputs to extract packet and RTT statistics.

    Attributes:
        LINUX_PACKET_MSG (str): The regex pattern for parsing packet statistics.
        LINUX_STATISTICS (str): The regex pattern for parsing RTT statistics.
        _api (object): An API object for executing command-line operations.
        _ip_address (str): The remote IP address to ping.
        deviation (float): The standard deviation of RTT.
    """

    LINUX_PACKET_MSG = (r"(\d+) packets transmitted, (\d+) received, "
                        r"(\d+)% packet loss")
    LINUX_STATISTICS = (r"rtt min/avg/max/mdev ="
                        r" ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms")

    def __init__(self, api):
        """
        Initializes the LinuxPing class with an API object.

        Args:
            api (object): An API object that provides access to remote system commands.
        """
        super().__init__()
        self._api = api
        self._ip_address = self._api.remote_ip
        self.deviation = 0

    def ping(self, count=4):
        """
        Sends a ping request to a remote IP address and parses the results.

        Args:
            count (int): The number of ping requests to send. Default is 4.

        Returns:
            bool: True if both packet and RTT statistics were successfully parsed, False otherwise.
        """
        try:
            dict_return = self._api.command_line(
                f'ping -c {count} {self._ip_address}')
            logger.debug(f'dict_return = {dict_return}')
            if dict_return:
                bool_msg = self._parse_packets(dict_return.get(6), self.LINUX_PACKET_MSG)
                bool_sts = self._parse_statistics(dict_return.get(7),
                                       self.LINUX_STATISTICS)
                return bool_msg and bool_sts
            
            raise ValueError("Failed to get ping response.")
        except ValueError as w:
            logger.warning(f'Warning: {w}')
        except Exception as e:
            logger.error(f'Error: {e}')
            raise
        return False

    def _parse_statistics(self, output, rtt_regex):
        """
        Parses RTT statistics from the ping command output.

        Args:
            output (str): The output of the ping command.
            rtt_regex (str): The regular expression pattern to match RTT statistics.

        Returns:
            bool: True if the RTT statistics were successfully parsed, False otherwise.
        """
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = float(match.group(1))
            self.average = float(match.group(2))
            self.maximum = float(match.group(3))
            self.deviation = float(match.group(4))
            return True
        else:
            logger.warning(f"RTT statistics parsing failed: {output}")
        return False

class WindowsPing(PingBase):
    """
    A class for handling ping operations on Windows systems.

    This class extends PingBase to provide an implementation of ping operations
    specifically for Windows-based systems. It parses Windows-specific ping command
    outputs to extract packet and RTT statistics.

    Attributes:
        WINDOWS_PACKET_MSG (str): The regex pattern for parsing packet statistics.
        WINDOWS_STATISTICS (str): The regex pattern for parsing RTT statistics.
        _api (object): An API object for executing command-line operations.
        _ip_address (str): The remote IP address to ping.
    """

    WINDOWS_PACKET_MSG = (r"Packets: Sent = (\d+), Received ="
                          r" (\d+), Lost = (\d+)")
    WINDOWS_STATISTICS = (r"Minimum = (\d+)ms, Maximum = (\d+)ms,"
                          r" Average = (\d+)ms")

    def __init__(self, api):
        """
        Initializes the WindowsPing class with an API object.

        Args:
            api (object): An API object that provides access to remote system commands.
        """
        super().__init__()
        self._api = api
        self._ip_address = self._api.remote_ip

    def ping(self, count=4):
        """
        Sends a ping request to a remote IP address and parses the results.

        Args:
            count (int): The number of ping requests to send. Default is 4.

        Returns:
            bool: True if the ping response was successfully parsed, False otherwise.
        """
        try:
            dict_return = self._api.command_line(
                f'ping -n {count} {self._ip_address}')
            logger.debug(f'dict_return = {dict_return}')
            if dict_return:
                self._parse_packets(dict_return.get(6),
                                    self.WINDOWS_PACKET_MSG)
                self._parse_statistics(dict_return.get(7),
                                       self.WINDOWS_STATISTICS)
                return True
            
            raise ValueError("Failed to get ping response.")
        except ValueError as w:
            logger.warning(f'Warning: {w}')
        except Exception as e:
            logger.error(f'Error: {e}')
            raise
        return False
    
    def _parse_statistics(self, output, rtt_regex):
        """
        Parses RTT statistics from the ping command output.

        Args:
            output (str): The output of the ping command.
            rtt_regex (str): The regular expression pattern to match RTT statistics.

        Returns:
            bool: True if the RTT statistics were successfully parsed, False otherwise.
        """
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = float(match.group(1))
            self.average = float(match.group(2))
            self.maximum = float(match.group(3))

        else:
            logger.warning(f"RTT statistics parsing failed: {output}")
