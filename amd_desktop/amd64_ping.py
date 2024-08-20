# Contents of amd_64_ping.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from amd_desktop.win10_interface import Win10Interface as win10

logger = logging.getLogger(__name__)

class AMD64Ping(object):
    def __init__(self):
        self._api = win10()
        self._ip_address = self._api.remote_ip
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0

    def ping(self, count=4) -> bool:
        try:
            dict_return = self._api.command_line(f'ping -n {count} {self._ip_address}')
            logger.debug(f'str_return = {dict_return}')
            if dict_return:
                self._parse_packets(dict_return.get(8))
                self._parse_statistics(dict_return.get(10))
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
        sent_received_lost_regex = r"Packets: Sent = (\d+), Received = (\d+), Lost = (\d+)"
        match = re.search(sent_received_lost_regex, output)
        if match:
            self.sent = int(match.group(1))
            self.received = int(match.group(2))
            self.lost = int(match.group(3))

    def _parse_statistics(self, output):
        # Extract Minimum, Maximum, Average round-trip times
        rtt_regex = r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms"
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = int(match.group(1))
            self.maximum = int(match.group(2))
            self.average = int(match.group(3))
