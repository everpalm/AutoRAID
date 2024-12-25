# Contents of test_win_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest
from amd_desktop.amd64_nvme import AMD64NVMe
from amd_desktop.amd64_partition import WindowsVolume

logger = logging.getLogger(__name__)

DISKPART = """
    list disk
    """

with open('config/test_win_partition.json', 'r', encoding='utf-8') as f:
    DISKPART = [json.load(f)]


class TestWindowsVolume:
    @pytest.fixture(scope="module")
    def win_partition(self, target_system: AMD64NVMe) -> WindowsVolume:
        """
        docstring
        """
        return WindowsVolume(platform=target_system)

    @pytest.mark.parametrize('diskpart', DISKPART)
    def test_write_script(self, win_partition: WindowsVolume, diskpart):
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
        # logger.debug("diskpart = %s", diskpart['List Disk']['Script'])
        result = win_partition.write_script(diskpart['List Disk']['Script'])
        logger.info('write_script = %s', result)

    @pytest.mark.parametrize('diskpart', DISKPART)
    def test_execute(self, win_partition: WindowsVolume, diskpart):
        """
        docstring
        """
        exe_result = win_partition.execute(diskpart['List Disk']['Pattern'])
        logger.info('exe_result = %s', exe_result)

    def test_delete_script(self, win_partition: WindowsVolume):
        '''
        docstring
        '''
        del_result = win_partition.delete_script()
        logger.info('del_result = %s', del_result)
