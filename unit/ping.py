'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from abc import ABC
from abc import abstractmethod

logger = logging.getLogger(__name__)

class PingBase(ABC):
    def __init__(self):
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0
        # self.deviation = 0

    @abstractmethod
    def ping(self, count=4):
        pass

    def _parse_packets(self, output, packet_regex):
        match = re.search(packet_regex, output)
        if match:
            self.sent = int(match.group(1))
            self.received = int(match.group(2))
            self.lost = self.sent - self.received  # Calculate packet loss
        else:
            logger.warning(f"Packet statistics parsing failed: {output}")


class LinuxPing(PingBase):
    LINUX_PACKET_MSG = (r"(\d+) packets transmitted, (\d+) received, "
                        r"(\d+)% packet loss")
    LINUX_STATISTICS = (r"rtt min/avg/max/mdev ="
                        r" ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms")

    def __init__(self, api):
        super().__init__()
        self._api = api
        self._ip_address = self._api.remote_ip
        self.deviation = 0

    def ping(self, count=4):
        try:
            dict_return = self._api.command_line(
                f'ping -c {count} {self._ip_address}')
            logger.debug(f'dict_return = {dict_return}')
            if dict_return:
                self._parse_packets(dict_return.get(6), self.LINUX_PACKET_MSG)
                self._parse_statistics(dict_return.get(7),
                                       self.LINUX_STATISTICS)
                return True
            raise ValueError("Failed to get ping response.")
        except ValueError as w:
            logger.warning(f'Warning: {w}')
        except Exception as e:
            logger.error(f'Error: {e}')
            raise
        return False

    def _parse_statistics(self, output, rtt_regex):
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = float(match.group(1))
            self.average = float(match.group(2))
            self.maximum = float(match.group(3))
            self.deviation = float(match.group(4))
        else:
            logger.warning(f"RTT statistics parsing failed: {output}")

class WindowsPing(PingBase):
    WINDOWS_PACKET_MSG = (r"Packets: Sent = (\d+), Received ="
                          r" (\d+), Lost = (\d+)")
    WINDOWS_STATISTICS = (r"Minimum = (\d+)ms, Maximum = (\d+)ms,"
                          r" Average = (\d+)ms")

    def __init__(self, api):
        super().__init__()
        self._api = api
        self._ip_address = self._api.remote_ip

    def ping(self, count=4):
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
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = float(match.group(1))
            self.average = float(match.group(2))
            self.maximum = float(match.group(3))

        else:
            logger.warning(f"RTT statistics parsing failed: {output}")
