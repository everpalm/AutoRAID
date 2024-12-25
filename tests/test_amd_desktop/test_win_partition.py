# Contents of test_win_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest
from amd_desktop.amd64_nvme import AMD64NVMe
from amd_desktop.amd64_partition import WindowsVolume

logger = logging.getLogger(__name__)


class TestWindowsVolume:
    @pytest.fixture(scope="module")
    def win_partition(self, target_system: AMD64NVMe) -> WindowsVolume:
        """
        docstring
        """
        return WindowsVolume(platform=target_system)

    def test_write_script(self, target_system, win_partition: WindowsVolume):
        """
        docstring
        """
        # DISKPART_SCRIPT = f"""
        #     select disk {target_system.disk_num}
        #     create partition primary
        #     format fs=ntfs quick
        #     assign
        #     exit
        #     """
        DISKPART_SCRIPT = """list disk"""
        result = win_partition.write_script(DISKPART_SCRIPT)
        logger.info('write_script = %s', result)

    def test_execute(self, win_partition: WindowsVolume):
        """
        docstring
        """
        result = win_partition.execute()
        logger.info('result = %s', result)

