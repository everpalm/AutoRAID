# Contents of arm/system.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import multiprocessing
from abc import ABC
from abc import abstractmethod
from amd64.system import BaseOS
from dataclasses import dataclass
from interface.application import BaseInterface
from typing import Tuple
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.DEBUG)


@dataclass
class CPUInformation:
    '''Context of CPU Information'''
    vendor_name: str
    model_name: str
    hyperthreading: bool


@dataclass
class SystemInformation:
    '''Context of System Information'''
    manufacturer: str
    model: str
    name: str
    rev: str


class BaseUART(ABC):
    _instance = None
    _lock = multiprocessing.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:  # 確保進程安全
                if cls._instance is None:  # 再次檢查，確保單例
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uart_path: str, baud_rate: int, file_name: str):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.uart_path = uart_path
            self.baud_rate = baud_rate
            self.file_name = file_name

    @abstractmethod
    def open_uart(self):
        pass

    @abstractmethod
    def close_uart(self):
        pass


class RaspberryPi(BaseOS, BaseUART):
    """
    Raspberry Pi UART Manager

    This class is responsible for opening and closing a UART session on
    a Raspberry Pi using the 'screen' command.

    Attributes:
        uart_device (str): The UART device path, e.g. '/dev/ttyAMA0'.
        baud_rate (int): The UART baud rate, e.g. 115200.
        logfile_path (str): The path to the logfile for 'screen'.
        api: An API interface to run command_line commands (e.g. SSH or local).
    """
    def __init__(self, uart_path: str, baud_rate: int, file_name: str,
                 rpi_api: BaseInterface):
        BaseOS.__init__(self, rpi_api)
        BaseUART.__init__(self, uart_path, baud_rate, file_name)

    def open_uart(self) -> None:
        try:
            logger.debug('self.file_name = %s', self.file_name)
            self.api.command_line('pwd')
            self.api.command_line(
                f"sudo screen -dm -L -Logfile "
                f"{self.file_name} {self.uart_path} "
                f"{self.baud_rate}"
            )
        except Exception as e:
            logger.warning("Failed to open UART session: %s", e)

    def close_uart(self) -> int:
        str_return = self.api.command_line("sudo screen -ls")
        logger.debug('str_return = %s', str_return)
        if not str_return:
            logger.warning("No screen sessions found (screen -ls is empty).")
            return -1
        try:
            uart_port = str_return.get(1).split('..')[0]
            logger.info(f'uart_port = {uart_port}')
            if not uart_port.isdigit():
                logger.warning("Cannot parse a valid UART port from: %s",
                               str_return)
                return -1
        except Exception as e:
            logger.error("Failed to parse UART port: %s", e)
            return -1

        close_cmd = self.api.command_line(
            f"sudo screen -X -S {uart_port} quit")
        logger.debug("Closing UART session with command: %s", close_cmd)
        return int(uart_port)

    def _get_memory_size(self) -> Tuple[int, str]:
        try:
            memory_info = self.api.command_line.original(
                self.api, "cat /proc/meminfo | grep MemTotal")
            split_info = memory_info[0].split()
            value, unit = split_info[1], split_info[2]
            return (int(value), unit)

        except Exception as e:
            logger.error("Failed to retrieve memory size: %s", str(e))
            raise

    def get_cpu_info(self) -> CPUInformation:
        try:

            cpu_manufacturer = self.api.command_line.original(
                self.api, "lscpu | grep 'Vendor ID'")

            cpu_model_name = self.api.command_line.original(
                self.api, "lscpu | grep 'Model name'")

            cpu_info = CPUInformation(
                cpu_manufacturer[0].split(':')[1],  # vendor name
                cpu_model_name[0].split(':')[1],    # model name
                False                               # hyperthreading
            )
            logger.debug("vendor_name = %s", cpu_info.vendor_name)
            logger.debug("model_name = %s", cpu_info.model_name)
            logger.debug("hyperthreading = %s", cpu_info.hyperthreading)

            # return vendor_name
            return cpu_info
        except Exception as e:
            logger.error("Failed to retrieve CPU info: %s", str(e))
            raise

    def get_system_info(self) -> SystemInformation:
        try:
            cpu_output = self.api.command_line.original(
                self.api, "cat /proc/cpuinfo | grep 'Model'")

            host_name = self.api.command_line.original(
                self.api, "hostname")

            system_info = SystemInformation(
                ' '.join(cpu_output[0].split()[2:5]),   # manufacturer
                ' '.join(cpu_output[0].split()[6:7]),   # model
                host_name[0],                           # name
                ' '.join(cpu_output[0].split()[8:9])    # Rev
            )
            logger.debug("manufacturer = %s", system_info.manufacturer)
            logger.debug("model = %s", system_info.model)
            logger.debug("name = %s", system_info.name)
            logger.debug("rev = %s", system_info.rev)

            # return vendor_name
            return system_info
        except Exception as e:
            logger.error("Failed to retrieve System info: %s", str(e))
            raise
