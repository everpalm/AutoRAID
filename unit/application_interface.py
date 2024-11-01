# Contents of application_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from typing import Tuple
from typing import List
from typing import Dict
import logging
import subprocess
import socket
import fcntl
import os
import struct
import json
import paramiko

SSH_PORT = '22'

''' Define NevoX application interface '''

logger = logging.getLogger(__name__)


def dict_format(callback):
    def wrapper(*args, **kwargs):
        dict_result = callback(*args, **kwargs)
        logger.debug("Result to be transformed = %s", dict_result)
        return dict(enumerate(dict_result))
    wrapper._original = callback
    return wrapper

# def json_format(callback):
#     def warp(*args, **kwargs):
#         return json.dumps(callback(*args, **kwargs))
#     return warp


class ApplicationInterface(ABC):
    ''' Application Interface

        This interface distinguish operations between the test script and
        DUT/SUT

        Attributes:
            mode: Remote - running on Ras-Pi; Local - running on SUT
            local_ip:
            remote_ip:
            account: Input the credential in SSH
            password: Input the password in SSH
            dir: The folder where lionapp is locationed
    '''
    def __init__(self, str_mode: str, str_if_name: str, str_config_file: str):
        self.mode = str_mode
        self.config_file = str_config_file
        self.if_name = str_if_name
        self.local_ip = self._get_local_ip(str_if_name)
        self.remote_ip, self.account, self.password, self.local_dir, \
            self.remote_dir = self._get_remote_ip()
        self.os = self.get_os()

    def __import_config(self) -> Dict[str, str]:
        try:
            with open(f'config/{self.config_file}', 'r') as f:
                list_config = json.load(f)
                if not isinstance(list_config, list):
                    raise ValueError(f"Expected dict in config file, got {type(list_config)}")
                return list_config
        except Exception:
            logger.error('Cannot open/read file: %s', self.config_file)
            raise

    @staticmethod
    def _get_local_ip(str_if_name: str) -> str:
        # Create a socket instance
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            local_ip = socket.inet_ntoa(
                fcntl.ioctl(
                    my_socket.fileno(), 0x8915, struct.pack(
                        '256s', bytes(str_if_name[:15], 'utf-8')))[20:24])
            logger.debug('local_ip = %s', local_ip)
        except socket.error:
            local_ip = None
            logger.error('Network disconnected')
        finally:
            # Close the socket connection
            my_socket.close()
        return local_ip

    def _get_remote_ip(self) -> Tuple[str]:
        remote_ip = None
        for dict_element in self.__import_config():
            # remote_ip = None
            if dict_element.get('Local') == self.local_ip:
                logger.debug('Found target dict_element = %s', dict_element)
                remote_ip = dict_element.get('Remote')
                str_account = dict_element.get('Account')
                str_password = dict_element.get('Password')
                str_local_dir = os.environ.get('WORKSPACE')
                str_remote_dir = dict_element.get('Remote Directory')
                logger.debug('remote_ip = %s', remote_ip)
                break
            else:
                logger.debug('Not target dict_element = %s', dict_element)
                continue
        if remote_ip is None:
            # raise ValueError('Remote network is disconnected')
            pass
            logger.debug('Local Mode Only')
        return remote_ip, str_account, str_password, str_local_dir, \
            str_remote_dir

    def get_ip_address(self) -> str:
        if self.mode == 'remote':
            return self._get_remote_ip()
        elif self.mode == 'local':
            return self._get_local_ip()

    @staticmethod
    def my_command(str_ssh_command: str) -> List[str]:
        __list_msg = []
        messages = subprocess.Popen(
            str_ssh_command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        str_msg_stdout = messages.stdout.readlines()

        for message in str_msg_stdout:
            if str(message, 'utf8') != '\n':
                log_msg = str(message, 'utf8').replace(
                    '\n', '').replace('\x08', '')
                logger.debug(f'{log_msg}')
                response_msg = ' '.join(str(message, 'utf8').split())
                __list_msg.append(response_msg.replace('\x08', ''))
        return __list_msg

    def get_os(self) -> str:
        ''' Get OS version
            Args: None
            Returns: OS type
            Raises: None
        '''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
        # 連線到遠端主機，使用預設的 SSH 端口（22）
            ssh.connect(self.remote_ip, SSH_PORT, self.account, self.password)
            os_info = ""

            # Try Linux uname command
            stdin, stdout, stderr = ssh.exec_command("uname -s")
            uname_output = stdout.read().decode('utf-8').strip()
            if uname_output:
                # os_info = f"Linux/Unix: {uname_output}"
                os_info = "Linux"
            else:
                # Try Windows systeminfo command
                stdin, stdout, stderr = ssh.exec_command("systeminfo")
                systeminfo_output = stdout.read().decode('utf-8').strip()
                if systeminfo_output:
                    # os_info = "Windows: " + "\n".join(systeminfo_output.split("\n")[:10])  # 只取前几行作为示例
                    os_info = "Windows"
            if not os_info:
                raise Exception("Failed to retrieve OS information")
            logger.debug('os_info = %s', os_info)
            return os_info
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        finally:
            ssh.close()
    
    # @dict_format
    def io_command(self, str_ssh_command: str) -> bool:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.remote_ip, username=self.account,
                       password=self.password)
        # stdin, stdout, stderr = client.exec_command(str_ssh_command,
        _, stdout, _ = client.exec_command(str_ssh_command,
                                                    get_pty=True)
        # for line in iter(stdout.readline, ""):
        #     logger.debug("line.strip() = %s", line.strip())
        output = stdout.read().decode()
        # bool_status = stdout.channel.recv_exit_status()
        if not stdout.channel.recv_exit_status():
                client.close()
        # client.close()
        # return bool_status
        return output

    def set_access_mode(self, str_mode: str):
        self.mode = str_mode
        if self.mode != 'local' and self.mode != 'remote':
            raise ValueError('Unknown mode setting in set_access_mode')

    @dict_format
    @abstractmethod
    def command_line(self, str_cli_cmd: str) -> list[str]:
        logger.debug('str_cli_cmd = %s', str_cli_cmd)
        logger.debug('self.mode = %s', self.mode)
        logger.debug('self.account = %s', self.account)
        logger.debug('self.password = %s', self.password)
        logger.debug('self.local_dir = %s', self.local_dir)
        logger.debug('self.remote_dir = %s', self.remote_dir)
        str_sshpass = (f'sshpass -p \"{self.password}\"'
                ' ssh -o \"StrictHostKeyChecking=no\"')
        logger.debug('str_sshpass = %s', str_sshpass)
        if self.mode == 'remote':
            logger.debug('===Remote access mode===')
            if self.os == 'Linux':
                logger.debug('===Linux===')
                str_command_line = (f'{str_sshpass}'
                    f' {self.account}@{self.remote_ip}'
                    f' \"cd {self.remote_dir};{str_cli_cmd}"')
            elif self.os == 'Windows':
                logger.debug('===Windows===')
                str_command_line = (f"{str_sshpass}"
                    f" {self.account}@{self.remote_ip}"
                    # f' \"cd {self.remote_dir}&&{str_cli_cmd}"')
                    f" 'cd {self.remote_dir}&&{str_cli_cmd}'")
        elif self.mode == 'local':
            logger.debug('===Local access mode===')
            # str_command_line = f'cd {self.local_dir};{str_cli_cmd}'
            str_command_line = f'{str_cli_cmd}'
        else:
            raise ValueError('Unknown mode setting in command_line')
        logger.debug('str_command_line = %s', str_command_line)
        return self.my_command(str_command_line)
