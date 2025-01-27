import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from interface.application import BaseInterface
from interface.application import WindowsInterface
from interface.application import InterfaceFactory


@pytest.fixture
def mock_base_interface_config():
    """Mock configuration data for BaseInterface."""
    return [
        {
            "Local": {
                "Operating System": {
                    "Type": "Linux",
                    "Version": "Raspbian GNU/Linux 11 (bullseye)",
                    "Account": "ste",
                    "Password": "123456"
                },
                "Software": {
                    "mnv_cli": {
                        "Path": "/home/pi/Projects/AutoRAID",
                        "Version": "1.0.0.1053"
                    },
                    "Script": {
                        "Path": "/home/pi/Projects/AutoRAID",
                        "Version": "0.0.1"
                    }
                },
                "Hardware": {
                    "Network": {
                        "IP": "192.168.0.100"
                    }
                }
            },
            "Remote": {
                "Operating System": {
                    "Type": "Windows",
                    "Version": "10.0.19045.5371",
                    "Account": "ste",
                    "Password": "123456"
                },
                "Software": {
                    "mnv_cli.exe": {
                        "Path": "C:\\Users\\STE\\Downloads\\YT01",
                        "Version": "1.0.0.1053"
                    },
                    "Script": {
                        "Path": "C:\\Users\\STE\\Projects\\AutoRAID",
                        "Version": "0.0.1"
                    }
                },
                "Hardware": {
                    "Network": {
                        "IP": "192.168.0.200"
                    },
                    "Storage": {
                        "Standard NVM Express Controller": {
                            "PCIE Configuration": {
                                "Manufacturer": "TestManufacturer",
                                "VID": "1B4B",
                                "DID": "22411B4B",
                                "SDID": "22411B4B",
                                "Rev": "20"
                            }
                        }
                    }
                }
            }
        }
    ]


# 測試 _get_local_ip 方法
def test_get_local_ip():
    with patch("socket.socket") as mock_socket, \
         patch("fcntl.ioctl") as mock_ioctl:
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.fileno.return_value = 0

        # 模擬返回的網絡接口數據
        mock_ioctl.return_value = \
            b"\x00" * 20 + b"\xC0\xA8\x00\x64" + b"\x00" * 212  # 192.168.0.100

        ip = BaseInterface._get_local_ip("eth0")
        assert ip == "192.168.0.100"


# 測試 _get_remote_ip1 方法
def test_get_remote_ip1(mock_base_interface_config):
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("interface.application.BaseInterface._get_local_ip",
               return_value="192.168.0.100"):

        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        result = interface._get_remote_ip1()

        assert result == (
            "192.168.0.200",
            "ste",
            "123456",
            None,
            "C:\\Users\\STE\\Projects\\AutoRAID",
            "TestManufacturer"
        )


# 測試 ftp_command 方法
def test_ftp_command_windows(mock_base_interface_config):
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("paramiko.SSHClient") as mock_ssh_client, \
         patch("interface.application.BaseInterface._get_local_ip",
               return_value="192.168.0.100"):

        mock_sftp = MagicMock()
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp

        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        result = interface.ftp_command("test_file.txt")
        assert result is True

        # 使用 os.path.join 確保測試中的路徑與方法一致
        expected_path = os.path.join("C:\\Users\\STE\\Projects\\AutoRAID",
                                     "diskpart_script.txt").replace("\\", "/")
        mock_sftp.put.assert_called_once_with("test_file.txt", expected_path)


# 測試 command_line 方法
def test_command_line_windows(mock_base_interface_config):
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch(
             "interface.application.WindowsInterface.my_command",
             return_value=["Command executed successfully"]
         ):

        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        result = interface.command_line("echo Test")
        assert result == {0: "Command executed successfully"}


# 測試創建接口方法
def test_create_windows_interface(mock_base_interface_config):
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("interface.application.BaseInterface._get_local_ip",
               return_value="192.168.0.100"):

        factory = InterfaceFactory()
        interface = factory.create_interface(
            os_type="Windows",
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        assert isinstance(interface, WindowsInterface)
        assert interface.remote_ip == "192.168.0.200"
