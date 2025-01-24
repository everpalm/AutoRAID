# Contents of arm/system.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from amd64.system import BaseOS
from interface.application import BaseInterface
from unit.log_handler import get_logger


logger = get_logger(__name__, logging.INFO)


class RaspberryPi(BaseOS):
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
        super().__init__(rpi_api)
        self.uart_path = uart_path
        self.baud_rate = baud_rate
        self.file_name = file_name

    def open_uart(self) -> None:
        logger.debug('self.file_name = %s', self.file_name)
        self.api.command_line('pwd')
        self.api.command_line(f"sudo screen -dm -L -Logfile {self.file_name}"
                              f" {self.uart_path} {self.baud_rate}")

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

    def _get_memory_size(self):
        pass

    def get_cpu_info(self):
        pass
