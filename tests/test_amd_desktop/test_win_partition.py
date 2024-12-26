# Contents of test_win_partition.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest
from amd_desktop.amd64_nvme import AMD64NVMe
from amd_desktop.amd64_partition import WindowsVolume

logger = logging.getLogger(__name__)

with open('config/test_win_partition.json', 'r', encoding='utf-8') as f:
    SCENARIO = json.load(f)


@pytest.fixture(scope="module")
def win_partition(target_system: AMD64NVMe) -> WindowsVolume:
    """
    docstring
    """
    return WindowsVolume(platform=target_system, disk_format='gpt',
                         file_system='ntfs')


class TestWindowsVolume:
    # @pytest.fixture(scope="module")
    # def win_partition(self, target_system: AMD64NVMe) -> WindowsVolume:
    #     """
    #     docstring
    #     """
    #     return WindowsVolume(platform=target_system, disk_format='gpt',
    #                          file_system='ntfs')

    @pytest.mark.parametrize('scenario', SCENARIO)
    def test_write_script(self, win_partition: WindowsVolume, scenario):
        """
        docstring
        """
        write_result = win_partition.write_script(
            scenario["Script"])
        logger.info('write_script = %s', write_result)
        assert write_result is True

        exe_result = win_partition.execute(scenario["Pattern"])
        logger.info('exe_result = %s', exe_result)
        assert exe_result == scenario["Expected"]

    def test_create_partition(self, win_partition: WindowsVolume):
        """
        docstring
        """
        create_result = win_partition.create_partition()
        assert create_result is True

    def test_execute(self, win_partition: WindowsVolume):
        """
        docstring
        """
        exe_result = win_partition.execute(
            r"(DiskPart successfully formatted the volume\.)")
        logger.info('exe_result = %s', exe_result)
        assert exe_result == "DiskPart successfully formatted the volume."

    def test_delete_script(self, win_partition: WindowsVolume):
        '''
        docstring
        '''
        del_result = win_partition.delete_script()
        logger.info('del_result = %s', del_result)
        assert del_result is True
