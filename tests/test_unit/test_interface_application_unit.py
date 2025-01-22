# Contents of tests/test_unit/test_amd64_interface_unit.py
'''Copyright (c) 2025 Jaron Cheng'''
import pytest
from unittest.mock import patch, MagicMock
from interface.application import WindowsInterface
from interface.application import LinuxInterface
from interface.application import InterfaceFactory


@pytest.fixture
def base_interface():
    '''docstring'''
    with patch('interface.application.BaseInterface._get_local_ip',
               return_value='192.168.0.139'):
        with patch(
            'interface.application.BaseInterface._get_remote_ip',
            return_value=(
                "192.168.0.128",
                "pi",
                "123456",
                "/home/pi/Projects/AutoRAID",
                "C:\\Users\\STE\\Projects\\AutoRAID"
            )
        ):
            return WindowsInterface(
                mode='remote',
                if_name='eth0',
                ssh_port='22',
                config_file='app_map.json'
            )


def test_get_local_ip(base_interface):
    '''docstring'''
    with patch(
        'interface.application.BaseInterface._get_local_ip'
    ) as mock_get_local_ip:
        mock_get_local_ip.return_value = '127.0.0.1'
        result = base_interface._get_local_ip('eth0')
        assert result == '127.0.0.1'


def test_get_remote_ip(base_interface):
    '''docstring'''
    with patch(
        'interface.application.BaseInterface._get_remote_ip'
    ) as mock_get_remote_ip:
        mock_get_remote_ip.return_value = (
            "192.168.0.128",
            "ste",
            "123456",
            "/home/pi/Projects/AutoRAID",
            "C:\\Users\\STE\\Projects\\AutoRAID"
        )
        result = base_interface._get_remote_ip()
        assert result == (
            "192.168.0.128",
            "ste",
            "123456",
            "/home/pi/Projects/AutoRAID",
            "C:\\Users\\STE\\Projects\\AutoRAID")


def test_os_type():
    '''docstring'''
    with patch('interface.application.paramiko.SSHClient') as mock_ssh_client:
        mock_ssh = MagicMock()
        mock_ssh.exec_command.return_value = (
            None,
            MagicMock(read=MagicMock(return_value=b"Linux")),
            None
        )
        mock_ssh_client.return_value = mock_ssh

        base_interface = WindowsInterface(
            mode='remote',
            if_name='eth0',
            ssh_port='22',
            config_file='app_map.json'
        )
        result = base_interface.os_type
        assert result == "Linux"


@pytest.fixture
def windows_interface():
    '''docstring'''
    return WindowsInterface(
        mode='remote',
        if_name='eth0',
        ssh_port='22',
        config_file='app_map.json'
    )


def test_ftp_command_windows(windows_interface):
    '''docstring'''
    # Mock 基類屬性，設置預期值
    with patch.object(windows_interface, 'remote_ip', '192.168.0.2'), \
         patch.object(windows_interface, 'account', 'user'), \
         patch.object(windows_interface, 'password', 'password'), \
         patch.object(windows_interface, 'remote_dir', '/remote'), \
         patch('interface.application.paramiko.SSHClient') as mock_ssh_client:

        # 模擬 SFTP 操作
        mock_ssh = MagicMock()
        mock_ssh.open_sftp.return_value.put.return_value = None
        mock_ssh_client.return_value = mock_ssh

        # 測試 ftp_command 方法
        result = windows_interface.ftp_command('test_file.txt')
        assert result is True


def test_command_line_windows(windows_interface):
    '''docstring'''
    with patch(
        'interface.application.WindowsInterface.my_command',
        return_value=['Command executed successfully']
    ) as mock_my_command:
        result = windows_interface.command_line('echo Test')
        # 確認結果是字典，且內容正確
        assert result == {0: 'Command executed successfully'}


@pytest.fixture
def linux_interface():
    '''docstring'''
    return LinuxInterface(
        mode='remote',
        if_name='eth0',
        ssh_port='22',
        config_file='app_map.json'
    )


def test_ftp_command_linux(linux_interface):
    '''docstring'''
    with patch.object(linux_interface, 'remote_ip', '192.168.0.2'), \
         patch.object(linux_interface, 'account', 'user'), \
         patch.object(linux_interface, 'password', 'password'), \
         patch.object(linux_interface, 'remote_dir', '/remote'), \
         patch('interface.application.paramiko.SSHClient') as mock_ssh_client:

        # Mock paramiko.SSHClient 行為
        mock_ssh = MagicMock()
        mock_sftp = mock_ssh.open_sftp.return_value
        mock_sftp.put.return_value = None
        mock_ssh_client.return_value = mock_ssh

        # 測試 ftp_command 方法
        result = linux_interface.ftp_command('test_file.txt')

        # 驗證結果
        assert result is True

        # 驗證 SFTP 操作是否正確執行
        mock_sftp.put.assert_called_once_with(
            'test_file.txt',
            '/remote/diskpart_script.txt'
        )
        mock_ssh.close.assert_called_once()


def test_command_line_linux(linux_interface):
    '''docstring'''
    with patch(
            'interface.application.LinuxInterface.my_command',
            return_value=['Command executed successfully']
    ) as mock_my_command:
        result = linux_interface.command_line('echo Test')
        assert result == {0: 'Command executed successfully'}


def test_create_windows_interface():
    '''docstring'''
    factory = InterfaceFactory()
    interface = factory.create_interface(
        os_type='Windows',
        mode='remote',
        if_name='eth0',
        ssh_port='22',
        config_file='app_map.json'
    )
    assert isinstance(interface, WindowsInterface)


def test_create_linux_interface():
    '''docstring'''
    factory = InterfaceFactory()
    interface = factory.create_interface(
        os_type='Linux',
        mode='remote',
        if_name='eth0',
        ssh_port='22',
        config_file='app_map.json'
    )
    assert isinstance(interface, LinuxInterface)


def test_create_invalid_interface():
    '''docstring'''
    factory = InterfaceFactory()
    with pytest.raises(ValueError):
        factory.create_interface(
            os_type='InvalidOS',
            mode='remote',
            if_name='eth0',
            ssh_port='22',
            config_file='app_map.json'
        )
