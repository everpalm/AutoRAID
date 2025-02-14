# Contents of interface/application.py
'''Copyright (c) 2024 Jaron Cheng'''
from __future__ import annotations  # Header, Python 3.7 or later version
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Tuple
from typing import List
from typing import Dict
from unit.json_handler import dict_format
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
    """Represents the context required to execute a remote command."""
    str_cli_cmd: str
    mode: str
    account: str
    password: str
    remote_dir: str
    remote_ip: str


@dataclass
class PCIeDevice:
    """Represents a generic PCIe device with ID, link width, and speed."""
    id: int
    link_width: str
    pcie_speed: str


@dataclass
class RootComplex(PCIeDevice):
    """Represents a PCIe Endpoint device."""


@dataclass
class EndPoint(PCIeDevice):
    """Represents a PCIe Endpoint device."""


@dataclass
class ConfigurationSpace:
    vid: str
    svid: str
    did: str
    sdid: str


@dataclass
class VirtualDrive:
    """Represents a virtual drive configuration.

    Attributes:
        vd_id: Virtual Drive ID.
        name: Name of the virtual drive.
        status: Current status of the virtual drive.
        importable: Whether the drive is importable.
        raid_mode: RAID mode used.
        size: Size of the drive.
        pd_count: Number of physical drives in the VD.
        pds: List of physical drive IDs.
        stripe_block_size: Stripe block size.
        sector_size: Sector size.
        total_of_vd: Total number of virtual drives.
    """
    vd_id: int
    name: str
    status: str
    importable: str
    raid_mode: str
    size: str
    pd_count: int
    pds: List[int]
    stripe_block_size: str
    sector_size: str
    bga_progress: str
    total_of_vd: int


@dataclass
class NVMeController(ConfigurationSpace):
    """Stores information about an NVMe controller.

    Attributes:
        bus_device_func: The bus, device, and function of the controller.
        device: Device identifier.
        slot_id: Slot identifier.
        firmware_version: Firmware version.
        vid: Vendor ID.
        svid: Subsystem Vendor ID.
        did: Device ID.
        sdid: Subsystem Device ID.
        revision_id: Revision ID.
        port_count: Number of ports.
        max_pd_of_per_vd: Max physical drives per virtual disk.
        max_vd: Maximum virtual disks supported.
        max_pd: Maximum physical drives supported.
        max_ns_of_per_vd: Max namespaces per virtual disk.
        max_ns: Maximum namespaces supported.
        supported_raid_mode: List of supported RAID modes.
        cache: Cache configuration.
        supported_bga_features: Background operation features supported.
        support_stripe_size: Supported stripe sizes.
        supported_features: List of other supported features.
        root_complexes: List of root complexes.
        end_points: List of endpoint devices.
    """
    bus_device_func: str
    device: str
    slot_id: str
    firmware_version: str
    revision_id: str
    port_count: int
    max_pd_of_per_vd: int
    max_vd: int
    max_pd: int
    max_ns_of_per_vd: int
    max_ns: int
    supported_raid_mode: List[str]
    cache: str
    supported_bga_features: List[str]
    support_stripe_size: List[str]
    supported_features: List[str]
    root_complexes: List[RootComplex] = field(default_factory=list)
    end_points: List[EndPoint] = field(default_factory=list)


@dataclass
class CPU:
    """docstring"""
    vendor: str
    model: str
    hyperthreading: bool
    cores: int


@dataclass
class System:
    """docstring"""
    manufacturer: str
    model: str
    name: str
    rev: str
    memory: str


@dataclass
class Network:
    """docstring"""
    ip: str
    mac_address: str


class BaseInterface(ABC):
    """Abstract base class defining the interface for system interaction."""
    def __init__(self, mode: str, if_name: str, ssh_port: str,
                 config_file: str):
        """Initializes the interface with network and configuration details.

        Args:
            mode: Operation mode (local/remote).
            if_name: Interface name.
            ssh_port: SSH port number.
            config_file: Configuration file name.
        """
        self.mode = mode
        self.config_file = config_file
        self.if_name = if_name
        self.ssh_port = ssh_port
        self.local_ip = self._get_local_ip(if_name)
        self.nvme_controller = None
        self.cpu = None
        self.system = None
        self.network = None
        self.virtual_drive = None
        (self.remote_ip, self.account, self.password, self.local_dir,
            self.remote_dir) = self._get_system_info()
        self._os_type = None
        self.script_name = "diskpart_script.txt"

    @abstractmethod
    def ftp_command(self, str_target_file: str) -> bool:
        """Handles FTP commands."""

    @abstractmethod
    def command_line(self, str_cli_cmd: str) -> str:
        """Executes a command-line command."""

    @abstractmethod
    def io_command(self, str_ssh_command: str) -> bool:
        """Executes I/O related commands over SSH."""

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
        list_msg = []
        messages = subprocess.Popen(
            str_ssh_command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        msg_stdout = messages.stdout.readlines()

        for message in msg_stdout:
            if str(message, 'utf8') != '\n':
                log_msg = str(message, 'utf8').replace(
                    '\n', '').replace('\x08', '')
                logger.debug('%s', log_msg)
                response_msg = ' '.join(str(message, 'utf8').split())
                list_msg.append(response_msg.replace('\x08', ''))
        return list_msg

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

    def _get_system_info(self) -> Tuple[str]:
        remote_ip = account = password = local_dir = remote_dir = None
        for element in self.__import_config():
            if element.get('Local').get('Hardware').get('Network').get('IP') \
                        == self.local_ip:
                logger.debug('Found target element = %s', element)
                hardware = element.get('Remote', {}).get('Hardware', {})
                local_os = element.get('Local', {}).get('Operating System')
                remote_sw = element.get('Remote', {}).get('Software')

                remote_ip = hardware['Network']['IP']
                account = local_os['Account']
                password = local_os['Password']
                local_dir = os.environ.get('WORKSPACE')
                remote_dir = remote_sw['Script']['Path']
                nvme_data = (
                    hardware['Storage']['NVMe Controller']
                )
                cpu_data = hardware['CPU']
                system_data = hardware['System']
                network_data = hardware['Network']
                root_complexes_list = [
                    RootComplex(**rc) for rc in nvme_data.get("root_complexes",
                                                              [])
                ]
                logger.debug("root_complexes_list = %s", root_complexes_list)
                end_points_list = [
                    EndPoint(**ep) for ep in nvme_data.get("end_points", [])
                ]
                logger.debug("end_points_list = %s", end_points_list)
                self.virtual_drive = [
                    VirtualDrive(**vd) for vd in nvme_data.get(
                        "Virtual Drive", [])
                ]
                self.nvme_controller = NVMeController(
                    vid=nvme_data["PCIE Configuration"]["VID"],
                    svid=nvme_data["PCIE Configuration"]["SVID"],
                    did=nvme_data["PCIE Configuration"]["DID"],
                    sdid=nvme_data["PCIE Configuration"]["SDID"],
                    bus_device_func=nvme_data["bus_device_func"],
                    device=nvme_data["device"],
                    slot_id=nvme_data["slot_id"],
                    firmware_version=nvme_data["firmware_version"],
                    revision_id=nvme_data["revision_id"],
                    port_count=nvme_data["port_count"],
                    max_pd_of_per_vd=nvme_data["max_pd_of_per_vd"],
                    max_vd=nvme_data["max_vd"],
                    max_pd=nvme_data["max_pd"],
                    max_ns_of_per_vd=nvme_data["max_ns_of_per_vd"],
                    max_ns=nvme_data["max_ns"],
                    supported_raid_mode=nvme_data["supported_raid_mode"],
                    cache=nvme_data["cache"],
                    supported_bga_features=nvme_data["supported_bga_features"],
                    support_stripe_size=nvme_data["support_stripe_size"],
                    supported_features=nvme_data["supported_features"],
                    root_complexes=root_complexes_list,
                    end_points=end_points_list
                )
                # Get CPU information
                self.cpu = CPU(
                    vendor=cpu_data["Vendor"],
                    model=cpu_data["Model Name"],
                    hyperthreading=cpu_data["Hyperthreading"],
                    cores=cpu_data["Core(s)"],
                )
                # Get system information
                self.system = System(
                    manufacturer=system_data["Manufacturer"],
                    model=system_data["Model"],
                    name=system_data["Name"],
                    rev=system_data["Rev"],
                    memory=system_data["Total Memory Size"]
                )
                # Get network information
                self.network = Network(
                    ip=network_data["IP"],
                    mac_address=network_data["MAC Address"]
                )
                logger.debug('cpu = %s', self.cpu)
                logger.debug('system = %s', self.system)
                logger.debug('network = %s', self.network)
                break

        if remote_ip is None:
            logger.debug('Local Mode Only')
        return remote_ip, account, password, local_dir, remote_dir

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
            logger.debug('================ Remote access mode ==============')
            return (
                f'{sshpass} {context.account}@{context.remote_ip} '
                f'"cd {context.remote_dir} && {context.str_cli_cmd}"'
            )
        elif context.mode == 'local':
            logger.debug('================ Local access mode ===============')
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

            remote_script_path = os.path.join(self.remote_dir,
                                              self.script_name).replace("\\",
                                                                        "/")
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
            logger.error("Error occurred in ftp_command: %s", e, exc_info=True)
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
    """Factory class to create interface instances based on the OS type."""

    def create_interface(self, os_type: str, **kwargs) -> BaseInterface:
        """Returns an instance of the appropriate interface based on OS type.

        Args:
            os_type: Operating system type (Windows/Linux).
            **kwargs: Additional arguments for initialization.

        Returns:
            An instance of WindowsInterface or LinuxInterface.
        """
        if os_type == 'Windows':
            return WindowsInterface(**kwargs)
        elif os_type == 'Linux':
            return LinuxInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")


class RaspberryInterfaceFactory(BaseInterfaceFactory):
    """Factory class to create interface instances based on the OS type."""
    def create_interface(self, os_type: str, **kwargs) -> BaseInterface:
        '''Factory method to create an interface based on OS type'''
        if os_type == 'Windows':
            return WindowsInterface(**kwargs)
        elif os_type == 'Linux':
            return LinuxInterface(**kwargs)
        else:
            raise ValueError(f"Unsupported OS type: {os_type}")
