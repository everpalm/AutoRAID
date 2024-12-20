# Contents of application_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
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
from unit.log_handler import get_logger

SSH_PORT = '22'

''' Define NevoX application interface '''

logger = get_logger(__name__, logging.INFO)


def dict_format(callback):
    """
    Decorator to convert the result of a function (which should return an
    iterable) to a dictionary with integer keys (index).

    This decorator wraps a given function, executes it, logs the result,
    and then converts the iterable returned by the original function to a
    dictionary where keys are the integer indices of the iterable's elements.

    Args:
        original_function: The function to be wrapped.

    Returns:
        Callable: The wrapped function.
        dict:  A dictionary where the keys are integer indices of the input
        list. Returns None if an error occurs during the dictionary creation.
    Raises:
         TypeError: If the input is not iterable

    """
    def wrapper(*args, **kwargs):
        """
        Wrapper function that executes the original function and formats the
        result as a dictionary.

        Args:
            *args: Variable length argument list of the original function.
            **kwargs: Arbitrary keyword arguments of the original function.

        Returns:
            Dict[int, Any] | None: A dictionary where the keys are integer
            indices of the original function's iterable result.
            Returns None if an error occurs during processing or the input is
            not iterable.

        Raises:
            TypeError: If the input function result is not iterable
        """
        try:
            dict_result = callback(*args, **kwargs)
            logger.debug("Result to be transformed = %s", dict_result)
            return dict(enumerate(dict_result))
        except TypeError as e:
            logger.error("TypeError occurred in wrapper: %s", e)
        except Exception as e:
            logger.exception("An unexpected error occurred in wrapper: %s", e)
            raise
    wrapper.original = callback
    return wrapper


@dataclass
class CommandContext:
    '''Context of an API command'''
    str_cli_cmd: str
    mode: str
    account: str
    password: str
    remote_dir: str
    remote_ip: str


class GenericAPI(ABC):
    '''This is a docstring'''
    @abstractmethod
    def cmd_transformer(self, context: CommandContext) -> str:
        '''Placeholder'''


class WindowsAPI(GenericAPI):
    @staticmethod
    def cmd_transformer(context: CommandContext) -> str:
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


class LinuxAPI(GenericAPI):
    '''This is a docstring'''
    @staticmethod
    def cmd_transformer(context: CommandContext) -> str:
        '''Placeholder'''
        logger.debug('Executing Linux cmd_transformer')
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


class ApplicationInterface:
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
    def __init__(self, str_mode: str, str_if_name: str, str_config_file: str,
                 interface: GenericAPI):
        '''This is a docstring'''
        self.mode = str_mode
        self.config_file = str_config_file
        self.if_name = str_if_name
        self.local_ip = self._get_local_ip(str_if_name)
        self.remote_ip, self.account, self.password, self.local_dir, \
            self.remote_dir = self._get_remote_ip()
        self.os = self.get_os()
        self.interface = interface

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
            os_info = None

            # Try Linux uname command
            # stdin, stdout, stderr = ssh.exec_command("uname -s")
            _, stdout, _ = ssh.exec_command("uname -s")
            uname_output = stdout.read().decode('utf-8').strip()
            if uname_output:
                # os_info = f"Linux/Unix: {uname_output}"
                os_info = "Linux"
            else:
                # Try Windows systeminfo command
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
            # return None
        finally:
            ssh.close()

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

        transformed_command = self.interface.cmd_transformer(context)
        logger.debug('Transformed Command: %s', transformed_command)

        return self.my_command(transformed_command)
