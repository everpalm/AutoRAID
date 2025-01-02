# Contents of commandline_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from abc import ABC
from abc import abstractmethod
from amd_desktop.amd64_system import BaseOS
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.DEBUG)


class BaseCLI(ABC):
    '''This is a docstring'''
    def __init__(self, platform: BaseOS):
        '''This is a docstring'''
        self.api = platform.api

    @abstractmethod
    def interpret(self, command: str) -> str:
        '''Placeholder'''


class WindowsCLI(BaseCLI):
    '''This is a docstring'''
    PREFIX = 'mnv_cli.exe'

    def interpret(self, command: str):
        '''placeholder'''

        try:
            composed_cmd = f'{self.PREFIX} {command}'
            logger.debug('composed_cmd = %s', composed_cmd)
            cmd_output = self.api.command_line.original(
                self.api,
                composed_cmd
            )
        except Exception as e:
            logger.error('Error occurred in interpretation: %s', str(e))
            raise
        return cmd_output


class LinuxCLI(WindowsCLI):
    '''This is a docstring'''
    PREFIX = 'mnv_cli'


class BaseCLIFactory(ABC):
    def __init__(self, api: BaseCLI):
        '''docstring'''
        self.api = api
        self.os_type = api.os_type

    @abstractmethod
    def initiate(self, **kwargs) -> BaseCLI:
        '''docstring'''
        pass


class CLIFactory(BaseCLIFactory):
    '''docstring'''
    def initiate(self, **kwargs) -> BaseCLI:
        '''docstring'''
        if self.os_type == 'Windows':
            return WindowsCLI(**kwargs)
        elif self.os_type == 'Linux':
            return LinuxCLI(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {self.os_type}")
