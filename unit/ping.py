# Contents of ping.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from unit.application_interface import ApplicationInterface as api
logger = logging.getLogger(__name__)

# LINUX_PACKET_MSG = (r"(\d+) packets transmitted, (\d+) received,"
#                      r"(\d+)% packet loss(\d+)")
LINUX_PACKET_MSG = (r"(\d+) packets transmitted, (\d+) received, "
                    r"(\d+)% packet loss")
LINUX_STATISTICS = (r"rtt min/avg/max/mdev = "
                    r"([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms")

class Ping(object):
    def __init__(self):
        self._api = api('local', 'eth0', 'app_map.json')
        self._ip_address = self._api.remote_ip
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0
        self.deviation = 0

    def ping(self, count=4):
        try:
            dict_return = self._api.command_line(f'ping -c {count} {self._ip_address}')
            logger.debug(f'str_return = {dict_return}')
            if dict_return:
                self._parse_packets(dict_return.get(6))
                self._parse_statistics(dict_return.get(7))
                return True
            raise ValueError(
                    "Failed to get ping response.")
        except ValueError as w:
            logger.warning(f'Warning: {w}')
            dict_return = None
        except Exception as e:
            logger.error(f'Error: {e}')
        return False

    def _parse_packets(self, output):
        # Extract Sent, Received, Lost
        sent_received_lost_regex = LINUX_PACKET_MSG
        match = re.search(sent_received_lost_regex, output)
        if match:
            self.sent = int(match.group(1))
            self.received = int(match.group(2))
            self.lost = self.sent - self.received
        else:
             logger.warning(f"Packet statistics parsing failed: {output}")
    
    def _parse_statistics(self, output):
        # Extract Minimum, Maximum, Average round-trip times
        rtt_regex = LINUX_STATISTICS
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = float(match.group(1))
            self.maximum = float(match.group(2))
            self.average = float(match.group(3))
            self.deviation = float(match.group(4))
        else:
            logger.warning(f"RTT statistics parsing failed: {output}")