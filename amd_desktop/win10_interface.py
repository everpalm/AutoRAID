# Contents of win10_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from unit.application_interface import ApplicationInterface
from unit.application_interface import dict_format
import logging
from typing import List
from typing import Dict

''' Define Win10 interface '''
# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


class Win10Interface(ApplicationInterface):

    # def __init__(self):
    #     super().__init__(str_mode='remote', str_if_name='eth0',
    #         str_config_file='app_map.json')

    @dict_format
    def command_line(self, str_cli_cmd: str) -> List[str]:
        logger.debug('str_cli_cmd = %s', str_cli_cmd)
        logger.debug('self.mode = %s', self.mode)
        logger.debug('self.account = %s', self.account)
        logger.debug('self.password = %s', self.password)
        logger.debug('self.local_dir = %s', self.local_dir)
        logger.debug('self.remote_dir = %s', self.remote_dir)
        logger.debug('self.os = %s', self.os)
        if self.mode == 'remote':
            logger.debug('===Remote access mode===')
            logger.debug('self.remote_ip = %s', self.remote_ip)
            str_sshpass = f'sshpass -p \"{self.password}\"'\
                ' ssh -o \"StrictHostKeyChecking=no\"'
            logger.debug('str_sshpass = %s', str_sshpass)
            str_command_line = f'{str_sshpass}'\
                f' {self.account}@{self.remote_ip}'\
                f' \"cd {self.remote_dir}&&{str_cli_cmd}\"'
            logger.debug('str_command_line = %s', str_command_line)
        elif self.mode == 'local':
            logger.debug('===Local access mode===')
            str_command_line = f'cd {self.local_dir}&&{str_cli_cmd}'
        else:
            raise ValueError('Unknown mode setting in command_line')
        return self.my_command(str_command_line)