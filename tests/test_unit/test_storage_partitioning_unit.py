# Content of tests/test_unit/test_storage_partitioning_unit.py
'''Copyright (c) 2025 Jaron Cheng'''
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest
from storage.partitioning import WindowsVolume
# from amd64.nvme import AMD64NVMe
from system.amd64 import AMD64Windows


@pytest.fixture
def mock_windows_platform():
    """Fixture to create a mocked AMD64NVMe platform for Windows tests."""
    mock_platform = MagicMock(spec=AMD64Windows)
    mock_platform.api = MagicMock()
    mock_platform.api.remote_dir = "/remote/dir"
    mock_platform.api.remote_ip = "192.168.1.100"
    mock_platform.api.account = "admin"
    mock_platform.api.password = "password"
    mock_platform.api.script_name = "diskpart_script.txt"

    # Mock command_line to return a valid dictionary
    mock_platform.api.command_line.return_value = {
        0: "0 Marvell_NVMe_Controller 1234567890"
    }

    mock_platform.disk_num = 0
    mock_platform.memory_size = 512
    mock_platform.manufacturer = "VEN_1B4B"  # Matches the manufacturer logic
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
    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
    with patch("builtins.open", side_effect=IOError("File error")):
        with pytest.raises(Exception,
                           match="Error during Windows disk partitioning"):
            windows_volume.write_script("dummy script")


def test_execute_success(mock_windows_platform):
    """Test executing a partition script successfully."""
    mock_output = [
        "Microsoft DiskPart version 10.0.19041.3636",
        "Disk 2 is now the selected disk."
    ]
    mock_windows_platform.api.command_line.original.return_value = mock_output
    pattern = r"Disk\s(\d+)"

    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
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

    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
    with pytest.raises(ValueError, match="No matching disk found"):
        windows_volume.execute(pattern)


def test_delete_script_success(mock_windows_platform):
    """Test deleting a disk partitioning script successfully."""
    mock_windows_platform.api.command_line.original.return_value = True

    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
    result = windows_volume.delete_script()

    # Assert the deletion was successful
    assert result is True


def test_delete_script_failure(mock_windows_platform):
    """Test failure during script deletion."""
    mock_windows_platform.api.command_line.original.side_effect = Exception(
        "Delete error")
    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')
    with pytest.raises(Exception,
                       match="Error during deletion of diskpart script"):
        windows_volume.delete_script()


def test_create_partition_success(mock_windows_platform):
    """Test creating partitions successfully."""
    mock_windows_platform.api.ftp_command = MagicMock()
    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')

    result = windows_volume.create_partition()

    # Assert the partition creation was successful
    assert result is True
    mock_windows_platform.api.ftp_command.assert_called_with(
        "diskpart_script.txt")


def test_create_partition_failure(mock_windows_platform):
    """Test failure during partition creation."""
    mock_windows_platform.api.ftp_command.side_effect = Exception("FTP error")

    windows_volume = WindowsVolume(mock_windows_platform, 'gpt', 'ntfs')

    with pytest.raises(Exception,
                       match="Error during creation of diskpart script"):
        windows_volume.create_partition()
