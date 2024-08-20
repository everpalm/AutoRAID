# Contents of ping.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from unit.application_interface import ApplicationInterface as api
logger = logging.getLogger(__name__)

class Ping(object):
    def __init__(self, ip_address):
        self._api = api('local', 'eth0', 'app_map.json')
        self._ip_address = self._api.remote_ip
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.minimum = 0
        self.maximum = 0
        self.average = 0

    def ping(self, count=4):
        try:
            dict_return = self._api.command_line(f'ping -c {count} {self._ip_address}')
            logger.debug(f'str_return = {dict_return}')
            if dict_return:
                self._parse_packets(dict_return.get(8))
                return True
            raise ValueError(
                    "Failed to get ping response.")
        except ValueError as w:
            logger.warning(f'Warning: {w}')
            dict_return = None
        except Exception as e:
            logger.error(f'Error: {e}')
        return False

    def _parse_ping_output(self, output):
        # Extract Sent, Received, Lost
        sent_received_lost_regex = r"Packets: Sent = (\d+), Received = (\d+), Lost = (\d+)"
        match = re.search(sent_received_lost_regex, output)
        if match:
            self.sent = int(match.group(1))
            self.received = int(match.group(2))
            self.lost = int(match.group(3))

        # Extract Minimum, Maximum, Average round-trip times
        rtt_regex = r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms"
        match = re.search(rtt_regex, output)
        if match:
            self.minimum = int(match.group(1))
            self.maximum = int(match.group(2))
            self.average = int(match.group(3))
