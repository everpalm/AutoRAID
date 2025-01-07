# Contents of commandline_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import re
from abc import ABC
from abc import abstractmethod
from amd_desktop.amd64_system import BaseOS
from dataclasses import dataclass
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.DEBUG)


@dataclass
class SMARTInfo:
    '''This is a docstring'''
    critical_warning: str
    composite_temp: str
    available_spare: str
    available_spare_threshold: str
    percentage_used: str


@dataclass
class BackendSMARTInfo(SMARTInfo):
    '''This is a docstring'''
    data_units_read: int
    data_units_written: int
    host_read_commands: int
    host_write_commands: int
    controller_busy_time: int
    power_cycles: int
    power_on_hours: int
    unsafe_shutdowns: int
    media_and_data_integrity_errors: int
    num_err_log_entries: int
    warning_composite_temp_time: int
    critical_composite_temp_time: int
    tmp_1_transition_count: int
    tmp_2_transition_count: int
    total_time_for_tmp1: int
    total_time_for_tmp2: int


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

    def get_controller_smart_info(self) -> SMARTInfo:
        try:
            smart_info = self.interpret('smart -o hba')
            string = ' '.join(smart_info)

            patterns = {
                "critical_warning": r"Critical Warning\s*:\s*(0x[0-9A-Fa-f]+)",
                "composite_temp": r"Composite Temperature\s*:\s*([0-9]+)",
                "available_spare": r"Available Spare\s*:\s*([0-9]+)",
                "available_spare_threshold": (
                    r"Available Spare Threshold\s*:\s*([0-9]+)"
                ),
                "percentage_used": r"Percentage Used\s*:\s*([0-9]+)"
            }
            result = {}

            for key, pattern in patterns.items():
                match = re.search(pattern, string)
                if match:
                    result[key] = match.group(1)
                    logger.debug(f"{key}: {result[key]}")
                else:
                    logger.warning(
                        "Pattern not matched in the command output.")
                    raise ValueError(f"No matching {key} found.")
            return SMARTInfo(**result)

        except re.error as e:
            logger.error("Error occurred in interpretation: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error during write script execution: %s", e)
            raise

    def get_backend_smart_info(self, pd_id: str) -> BackendSMARTInfo:
        try:
            smart_info = self.interpret(f'smart -i {pd_id}')
            string = ' '.join(smart_info)

            patterns = {
                "critical_warning": r"Critical Warning\s*:\s*(0x[0-9A-Fa-f]+)",
                "composite_temp": r"Composite Temperature\s*:\s*([0-9]+)",
                "available_spare": r"Available Spare\s*:\s*([0-9]+)",
                "available_spare_threshold": (
                    r"Available Spare Threshold\s*:\s*([0-9]+)"
                ),
                "percentage_used": r"Percentage Used\s*:\s*([0-9]+)",
                "data_units_read": r"Data Units Read\s*:\s*([0-9]+)",
                "data_units_written": r"Data Units Written\s*:\s*([0-9]+)",
                "host_read_commands": r"Host Read Commands\s*:\s*([0-9]+)",
                "host_write_commands": r"Host Write Commands\s*:\s*([0-9]+)",
                "controller_busy_time": r"Controller Busy Time\s*:\s*([0-9]+)",
                "power_cycles": r"Power Cycles\s*:\s*([0-9]+)",
                "power_on_hours": r"Power On Hours\s*:\s*([0-9]+)",
                "unsafe_shutdowns": r"Unsafe Shutdowns\s*:\s*([0-9]+)",
                "media_and_data_integrity_errors": (
                    r"Media and Data Integrity Errors\s*:\s*([0-9]+)"
                ),
                "num_err_log_entries": r"Num Err Log Entries\s*:\s*([0-9]+)",
                "warning_composite_temp_time": (
                    r"Warning Composite Temperature Time\s*:\s*([0-9]+)"
                ),
                "critical_composite_temp_time": (
                    r"Critical Composite Temperature Time\s*:\s*([0-9]+)"
                ),
                "tmp_1_transition_count": (
                    r"Temperature 1 Transition Count\s*:\s*([0-9]+)"
                ),
                "tmp_2_transition_count": (
                    r"Temperature 2 Transition Count\s*:\s*([0-9]+)"
                ),
                "total_time_for_tmp1": (
                    r"Total Time For Thermal Management Temperature "
                    r"1\s*:\s*([0-9]+)"
                ),
                "total_time_for_tmp2": (
                    r"Total Time For Thermal Management Temperature "
                    r"2\s*:\s*([0-9]+)"
                )
            }
            result = {}

            for key, pattern in patterns.items():
                match = re.search(pattern, string)
                if match:
                    result[key] = match.group(1)
                    logger.debug(f"{key}: {result[key]}")
                else:
                    logger.warning(
                        "Pattern not matched in the command output.")
                    raise ValueError(f"No matching {key} found.")
            return BackendSMARTInfo(**result)

        except re.error as e:
            logger.error("Error occurred in interpretation: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error during write script execution: %s", e)
            raise


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
