import pytest
from unittest.mock import MagicMock, patch
from amd_desktop.amd64_partition import WindowsVolume
from amd_desktop.amd64_nvme import AMD64NVMe


@pytest.fixture
def mock_windows_platform():
    """Fixture to create a mocked AMD64NVMe platform for Windows tests."""
    mock_platform = MagicMock(spec=AMD64NVMe)
    # 顯式添加 `api` 和其屬性
    mock_platform.api = MagicMock()
    mock_platform.api.remote_dir = "/remote/dir"
    mock_platform.api.remote_ip = "192.168.1.100"
    mock_platform.api.account = "admin"
    mock_platform.api.password = "password"
    mock_platform.api.script_name = "diskpart_script.txt"
    mock_platform.api.command_line.original = MagicMock()
    return mock_platform


@pytest.fixture
def mock_linux_platform():
    """Fixture to create a mocked AMD64NVMe platform for Linux tests."""
    mock_platform = MagicMock(spec=AMD64NVMe)
    # 添加 api 和相關方法
    mock_platform.api = MagicMock()
    mock_platform.api.command_line = MagicMock()
    return mock_platform


def test_write_script_success(mock_windows_platform):
    """Test writing a disk partitioning script successfully."""
    diskpart_script = "select disk 0\nclean\ncreate partition primary"
    mock_windows_platform.api.ftp_command = MagicMock()

    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
    result = windows_volume.write_script(diskpart_script)

    # Assert file writing and FTP upload were successful
    assert result is True
    mock_windows_platform.api.ftp_command.assert_called_with(
        "diskpart_script.txt")


def test_write_script_failure(mock_windows_platform):
    """Test failure during script writing."""
    windows_volume = WindowsVolume(mock_windows_platform)
    with patch("builtins.open", side_effect=IOError("File error")):
        with pytest.raises(
            Exception, match="Error during Windows disk partitioning"
        ):
            windows_volume.write_script("dummy script")


def test_execute_success(mock_windows_platform):
    """Test executing a partition script successfully."""
    mock_output = [
        "Microsoft DiskPart version 10.0.19041.3636",
        "Disk 2 is now the selected disk."
    ]
    mock_windows_platform.api.command_line.original.return_value = mock_output
    pattern = r"Disk\s(\d+)"

    windows_volume = WindowsVolume(mock_windows_platform)
    result = windows_volume.execute(pattern)

    # Assert the extracted value matches the expected result
    assert result == "2"


def test_execute_no_match(mock_windows_platform):
    """Test execute method with no matching pattern."""
    mock_output = [
        "Microsoft DiskPart version 10.0.19041.3636",
        "No disks found."
    ]
    mock_windows_platform.api.command_line.original.return_value = mock_output
    pattern = r"Disk\s(\d+)"

    windows_volume = WindowsVolume(mock_windows_platform)
    with pytest.raises(ValueError, match="No matching disk found"):
        windows_volume.execute(pattern)


def test_delete_script_success(mock_windows_platform):
    """Test deleting a disk partitioning script successfully."""
    mock_windows_platform.api.command_line.original.return_value = True

    windows_volume = WindowsVolume(mock_windows_platform)
    result = windows_volume.delete_script()

    # Assert the deletion was successful
    assert result is True


def test_delete_script_failure(mock_windows_platform):
    """Test failure during script deletion."""
    mock_windows_platform.api.command_line.original.side_effect = Exception(
        "Delete error")
    windows_volume = WindowsVolume(mock_windows_platform)
    with pytest.raises(Exception,
                       match="Error during deletion of diskpart script"):
        windows_volume.delete_script()