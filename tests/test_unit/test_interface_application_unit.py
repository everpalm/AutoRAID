import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from interface.application import (
    BaseInterface,
    WindowsInterface,
    LinuxInterface,
    InterfaceFactory
)


@pytest.fixture
def mock_base_interface_config():
    """Mock configuration data for BaseInterface."""
    return [
        {
            "Local": {
                "Hardware": {
                    "Network": {"IP": "192.168.0.100"}
                },
                "Operating System": {
                    "Account": "test_user",
                    "Password": "test_pass"
                }
            },
            "Remote": {
                "Hardware": {
                    "Network": {"IP": "192.168.0.200"},
                    "Storage": {
                        "Standard NVM Express Controller": {
                            "PCIE Configuration": {
                                "Manufacturer": "TestManufacturer"
                            }
                        }
                    }
                },
                "Software": {
                    "Script": {"Path": "/remote/scripts"}
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
        mock_ioctl.return_value = b"\x00" * 20 + b"\xC0\xA8\x00\x64" + b"\x00" * 212  # 192.168.0.100

        ip = BaseInterface._get_local_ip("eth0")
        assert ip == "192.168.0.100"


def test_get_remote_ip1(mock_base_interface_config):
    """Test the _get_remote_ip1 method."""
    mock_config_content = json.dumps(mock_base_interface_config)

    # Mock 文件內容
    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("interface.application.BaseInterface._BaseInterface__import_config") as mock_import_config, \
         patch("interface.application.BaseInterface._get_local_ip", return_value="192.168.0.100"):

        # 設置返回的配置數據
        mock_import_config.return_value = mock_base_interface_config

        # 初始化接口
        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        # 調用方法
        result = interface._get_remote_ip1()

        # 驗證返回值
        assert result == (
            "192.168.0.200",       # Remote IP
            "test_user",           # Account
            "test_pass",           # Password
            None,                  # Local directory
            "/remote/scripts",     # Remote directory
            "TestManufacturer"     # Manufacturer
        )


def test_ftp_command_windows(mock_base_interface_config):
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("paramiko.SSHClient") as mock_ssh_client, \
         patch("interface.application.BaseInterface._BaseInterface__import_config", return_value=mock_base_interface_config), \
         patch("interface.application.BaseInterface._get_local_ip", return_value="192.168.0.100"), \
         patch("interface.application.WindowsInterface._get_remote_ip1", return_value=(
             "192.168.0.200",
             "test_user",
             "test_pass",
             None,
             "/remote/scripts",
             "TestManufacturer"
         )):

        mock_sftp = MagicMock()
        mock_ssh_client.return_value.open_sftp.return_value = mock_sftp

        # 初始化接口
        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        # 測試 ftp_command 方法
        result = interface.ftp_command("test_file.txt")

        # 驗證結果
        assert result is True
        mock_sftp.put.assert_called_once_with("test_file.txt", "/remote/scripts/diskpart_script.txt")


# 測試 command_line 方法
def test_command_line_windows(mock_base_interface_config):
    """Test the command_line method in WindowsInterface."""
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch(
             "interface.application.WindowsInterface.my_command",
             return_value=["Command executed successfully"]
         ) as mock_my_command, \
         patch("interface.application.WindowsInterface._get_remote_ip1", return_value=(
             "192.168.0.200",
             "test_user",
             "test_pass",
             None,
             "/remote/scripts",
             "TestManufacturer"
         )), \
         patch("interface.application.BaseInterface._get_local_ip", return_value="192.168.0.100"):

        # 初始化接口
        interface = WindowsInterface(
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        # 調用 command_line 方法
        result = interface.command_line("echo Test")

        # 驗證返回值（期望字典格式）
        assert result == {0: "Command executed successfully"}

        # 驗證 my_command 被正確調用
        mock_my_command.assert_called_once_with(
            'sshpass -p "test_pass" ssh -o "StrictHostKeyChecking=no" test_user@192.168.0.200 "cd /remote/scripts && echo Test"'
        )


def test_create_windows_interface(mock_base_interface_config):
    """Test InterfaceFactory creates a WindowsInterface."""
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("interface.application.BaseInterface._BaseInterface__import_config", return_value=mock_base_interface_config), \
         patch("interface.application.BaseInterface._get_local_ip", return_value="192.168.0.100"), \
         patch("interface.application.WindowsInterface._get_remote_ip1", return_value=(
             "192.168.0.200",
             "test_user",
             "test_pass",
             None,
             "/remote/scripts",
             "TestManufacturer"
         )):
 
        # 初始化工廠
        factory = InterfaceFactory()

        # 創建 WindowsInterface
        interface = factory.create_interface(
            os_type="Windows",
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        # 驗證對象類型
        assert isinstance(interface, WindowsInterface)

        # 驗證初始化屬性
        assert interface.remote_ip == "192.168.0.200"
        assert interface.account == "test_user"
        assert interface.password == "test_pass"
        assert interface.remote_dir == "/remote/scripts"
        assert interface.manufacturer == "TestManufacturer"


def test_create_linux_interface(mock_base_interface_config):
    """Test InterfaceFactory creates a LinuxInterface."""
    mock_config_content = json.dumps(mock_base_interface_config)

    with patch("builtins.open", mock_open(read_data=mock_config_content)), \
         patch("interface.application.BaseInterface._BaseInterface__import_config", return_value=mock_base_interface_config), \
         patch("interface.application.BaseInterface._get_local_ip", return_value="192.168.0.100"), \
         patch("interface.application.LinuxInterface._get_remote_ip1", return_value=(
             "192.168.0.200",
             "test_user",
             "test_pass",
             None,
             "/remote/scripts",
             "TestManufacturer"
         )):
        
        # 初始化 InterfaceFactory
        factory = InterfaceFactory()

        # 創建 LinuxInterface
        interface = factory.create_interface(
            os_type="Linux",
            mode="local",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )

        # 驗證對象類型
        assert isinstance(interface, LinuxInterface)

        # 驗證初始化屬性
        assert interface.remote_ip == "192.168.0.200"
        assert interface.account == "test_user"
        assert interface.password == "test_pass"
        assert interface.remote_dir == "/remote/scripts"
        assert interface.manufacturer == "TestManufacturer"


# 測試 InterfaceFactory 創建無效接口
def test_create_invalid_interface():
    factory = InterfaceFactory()
    with pytest.raises(ValueError, match="Unsupported OS type: MacOS"):
        factory.create_interface(
            os_type="MacOS",
            mode="remote",
            if_name="eth0",
            ssh_port="22",
            config_file="test_config.json"
        )
