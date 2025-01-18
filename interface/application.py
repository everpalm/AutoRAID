# Contents of interface.application.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple
from typing import List
from typing import Dict
from interface.application_interface import dict_format
import logging
import subprocess
import socket
import fcntl
import os
import struct
import json
import paramiko
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


@dataclass
class CommandContext:
    '''Context of a command package'''
    str_cli_cmd: str
    mode: str
    account: str
    password: str
    remote_dir: str
    remote_ip: str


class BaseInterface(ABC):
    '''This is a docstring'''
    def __init__(self, mode: str, if_name: str, ssh_port: str,
                 config_file: str):
        '''This is a docstring'''
        self.mode = mode
        self.config_file = config_file
        self.if_name = if_name
        self.ssh_port = ssh_port
        self.local_ip = self._get_local_ip(if_name)
        self.remote_ip, self.account, self.password, self.local_dir, \
            self.remote_dir = self._get_remote_ip()
        self._os_type = None
        self.script_name = "diskpart_script.txt"

    @abstractmethod
    def ftp_command(self, str_target_file: str) -> bool:
        '''Placeholder'''

    @abstractmethod
    def command_line(self, str_cli_cmd: str) -> str:
        '''placeholder'''

    @abstractmethod
    def io_command(self, str_ssh_command: str) -> bool:
        '''Placeholder'''

    def __import_config(self) -> Dict[str, str]:
        '''This is a docstring'''
        try:
            with open(f'config/{self.config_file}', 'r',
                      encoding='us-ascii') as f:
                list_config = json.load(f)
                if not isinstance(list_config, list):
                    raise ValueError(f"Expected dict in config file, got "
                                     f"{type(list_config)}")
                return list_config
        except Exception:
            logger.error('Cannot open/read file: %s', self.config_file)
            raise

    @staticmethod
    def my_command(str_ssh_command: str) -> List[str]:
        '''Placeholder'''
        __list_msg = []
        messages = subprocess.Popen(
            str_ssh_command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        str_msg_stdout = messages.stdout.readlines()

        for message in str_msg_stdout:
            if str(message, 'utf8') != '\n':
                log_msg = str(message, 'utf8').replace(
                    '\n', '').replace('\x08', '')
                logger.debug('%s', log_msg)
                response_msg = ' '.join(str(message, 'utf8').split())
                __list_msg.append(response_msg.replace('\x08', ''))
        return __list_msg

    @staticmethod
    def _get_local_ip(str_if_name: str) -> str:
        '''This is a docstring'''
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
        '''This is a docstring'''
        remote_ip = str_account = str_password = str_local_dir = \
            str_remote_dir = None
        for dict_element in self.__import_config():
            if dict_element.get('Local') == self.local_ip:
                logger.debug('Found target dict_element = %s', dict_element)
                remote_ip = dict_element.get('Remote')
                str_account = dict_element.get('Account')
                str_password = dict_element.get('Password')
                str_local_dir = os.environ.get('WORKSPACE')
                str_remote_dir = dict_element.get('Remote Directory')
                logger.debug('remote_ip = %s', remote_ip)
                break

            logger.debug('Not target dict_element = %s', dict_element)
            continue
        if remote_ip is None:
            # raise ValueError('Remote network is disconnected')
            logger.debug('Local Mode Only')
        return (remote_ip, str_account, str_password, str_local_dir,
                str_remote_dir)

    def get_ip_address(self) -> str:
        '''This is a docstring'''
        if self.mode == 'remote':
            return self._get_remote_ip()
        elif self.mode == 'local':
            return self._get_local_ip()
        raise ValueError('Unknown mode')

    @property
    def os_type(self) -> str:
        ''' Get OS version
            Args: None
            Returns: OS type
            Raises: None
        '''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.remote_ip, self.ssh_port, self.account,
                        self.password)
            os_info = None

            _, stdout, _ = ssh.exec_command("uname -s")
            uname_output = stdout.read().decode('utf-8').strip()
            if uname_output:
                os_info = "Linux"
            else:
                _, stdout, _ = ssh.exec_command("systeminfo")
                systeminfo_output = stdout.read().decode('utf-8').strip()
                if systeminfo_output:
                    os_info = "Windows"
            if not os_info:
                raise ValueError("Failed to retrieve OS information")
            logger.debug('os_info = %s', os_info)
            return os_info

        except Exception as e:
            logger.error("OS Error: %s", e)
            raise

        finally:
            ssh.close()


class WindowsInterface(BaseInterface):
    '''This is a docstring'''
    def cmd_transformer(self, context: CommandContext) -> str:
        '''Placeholder'''
        logger.debug('Executing Windows cmd_transformer')
        sshpass = (
            f'sshpass -p "{context.password}" ssh -o '
            f'"StrictHostKeyChecking=no"'
        )
        if context.mode == 'remote':
            logger.debug('===Remote access mode===')
            return (
                f'{sshpass} {context.account}@{context.remote_ip} '
                f'"cd {context.remote_dir} && {context.str_cli_cmd}"'
            )
        elif context.mode == 'local':
            logger.debug('===Local access mode===')
            return context.str_cli_cmd
        else:
            raise ValueError('Unknown mode setting in command_line')

    def ftp_command(self, str_target_file: str) -> bool:
        '''Placeholder'''
        logger.debug('str_target_file: %s', str_target_file)
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.debug('remote_ip = %s', self.remote_ip)
            logger.debug('account = %s', self.account)
            logger.debug('password = %s', self.password)
            logger.debug('remote_dir = %s', self.remote_dir)

            remote_script_path = (
                self.remote_dir.replace("\\", "/") + f"/{self.script_name}")
            logger.debug('remote_script_path = %s', remote_script_path)
            client.connect(self.remote_ip, port=22, username=self.account,
                           password=self.password)

            sftp = client.open_sftp()
            logger.debug('sftp = %s', sftp)
            put_result = sftp.put(str_target_file, remote_script_path)
            logger.debug('put_result = %s', put_result)
            sftp.close()
            client.close()
        except Exception as e:
            logger.error("Error occurred in ftp_command: %s", e)
            raise
        return True

    @dict_format
    def command_line(self, str_cli_cmd: str) -> str:
        '''Placeholder'''
        context = CommandContext(
            str_cli_cmd=str_cli_cmd,
            mode=self.mode,
            account=self.account,
            password=self.password,
            remote_dir=self.remote_dir,
            remote_ip=self.remote_ip
        )
        logger.debug('CommandContext: %s', context.__dict__)

        transformed_command = self.cmd_transformer(context)
        logger.debug('Transformed Command: %s', transformed_command)

        return self.my_command(transformed_command)

    def io_command(self, str_ssh_command: str) -> bool:
        '''Placeholder'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.remote_ip, username=self.account,
                       password=self.password)

        _, stdout, _ = client.exec_command(str_ssh_command,
                                           get_pty=True)

        output = stdout.read().decode()

        if not stdout.channel.recv_exit_status():
            client.close()

        return output

    def set_access_mode(self, str_mode: str):
        '''This is a docstring'''
        self.mode = str_mode
        if self.mode != 'local' and self.mode != 'remote':
            raise ValueError('Unknown mode setting in set_access_mode')

    def ftp_get(self, file_name: str) -> bool:
        """
        Downloads a file from the remote server to the local system.

        :param remote_file_path: The full path of the file on the remote server
        :param local_file_path: The full path where the file will be saved
        locally
        :return: True if the file is downloaded successfully, otherwise raises
        an error
        """
        logger.debug('file_name: %s', file_name)

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.debug('remote_ip = %s', self.remote_ip)
            logger.debug('account = %s', self.account)
            logger.debug('password = %s', self.password)
            logger.debug('remote_dir = %s', self.remote_dir)

            # Connect to the remote server
            client.connect(self.remote_ip, port=22, username=self.account,
                           password=self.password)

            sftp = client.open_sftp()
            logger.debug('sftp = %s', sftp)

            if self.remote_dir:
                logger.debug('Change remote directory to: %s', self.remote_dir)
                sftp.chdir(self.remote_dir)

            # Download the file
            get_result = sftp.get(file_name, f"logs/{file_name}")
            logger.debug('get_result = %s', get_result)

            sftp.close()
            client.close()
        except Exception as e:
            logger.error("Error occurred in ftp_get: %s", e)
            raise
        return True


class LinuxInterface(BaseInterface):
    '''This is a docstring'''
    def cmd_transformer(self, context: CommandContext) -> str:
        '''Placeholder'''
        logger.debug('Executing Linux cmd_transformer, context.mode = %s',
                     context.mode)
        sshpass = (
            f'sshpass -p "{context.password}" ssh -o '
            f'"StrictHostKeyChecking=no"'
        )
        if context.mode == 'remote':
            logger.debug('===Remote access mode===')
            return (
                f'{sshpass} {context.account}@{context.remote_ip} '
                f'"cd {context.remote_dir}; {context.str_cli_cmd}"'
            )
        elif context.mode == 'local':
            logger.debug('===Local access mode===')
            return context.str_cli_cmd
        else:
            raise ValueError('Unknown mode setting in command_line')

    def ftp_command(self, str_target_file: str) -> bool:
        '''Placeholder'''
        logger.debug('str_target_file: %s', str_target_file)
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.debug('remote_ip = %s', self.remote_ip)
            logger.debug('account = %s', self.account)
            logger.debug('password = %s', self.password)
            logger.debug('remote_dir = %s', self.remote_dir)

            remote_script_path = (
                self.remote_dir.replace("\\", "/") + f"/{self.script_name}")
            logger.debug('remote_script_path = %s', remote_script_path)
            client.connect(self.remote_ip, port=22, username=self.account,
                           password=self.password)

            sftp = client.open_sftp()
            logger.debug('sftp = %s', sftp)
            put_result = sftp.put(str_target_file, remote_script_path)
            logger.debug('put_result = %s', put_result)
            sftp.close()
            client.close()
        except Exception as e:
            logger.error("Error occurred in ftp_command: %s", e)
            raise
        return True

    @dict_format
    def command_line(self, str_cli_cmd: str) -> str:
        '''Placeholder'''
        logger.debug('Preparing CommandContext for execution')
        context = CommandContext(
            str_cli_cmd=str_cli_cmd,
            mode=self.mode,
            account=self.account,
            password=self.password,
            remote_dir=self.remote_dir,
            remote_ip=self.remote_ip
        )
        logger.debug('CommandContext: %s', context.__dict__)

        transformed_command = self.cmd_transformer(context)
        logger.debug('Transformed Command: %s', transformed_command)

        return self.my_command(transformed_command)

    def io_command(self, str_ssh_command: str) -> bool:
        '''Placeholder'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.remote_ip, username=self.account,
                       password=self.password)

        _, stdout, _ = client.exec_command(str_ssh_command,
                                           get_pty=True)

        output = stdout.read().decode()

        if not stdout.channel.recv_exit_status():
            client.close()

        return output

    def set_access_mode(self, str_mode: str):
        '''This is a docstring'''
        self.mode = str_mode
        if self.mode != 'local' and self.mode != 'remote':
            raise ValueError('Unknown mode setting in set_access_mode')


class BaseInterfaceFactory(ABC):
    '''docstring'''
    @abstractmethod
    def create_interface(self) -> BaseInterface:
        pass


class InterfaceFactory(BaseInterfaceFactory):
    '''docstring'''
    def create_interface(self, os_type: str, **kwargs) -> BaseInterface:
        '''Factory method to create an interface based on OS type'''
        if os_type == 'Windows':
            return WindowsInterface(**kwargs)
        elif os_type == 'Linux':
            return LinuxInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")


class RaspberryInterfaceFactory(BaseInterfaceFactory):
    '''docstring'''
    def create_interface(self, os_type: str, **kwargs) -> BaseInterface:
        '''Factory method to create an interface based on OS type'''
        if os_type == 'Windows':
            return WindowsInterface(**kwargs)
        elif os_type == 'Linux':
            return LinuxInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")
