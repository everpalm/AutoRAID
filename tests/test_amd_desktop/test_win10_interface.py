# Contents of test_win10_interface.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest

''' Set up logger '''
logger = logging.getLogger(__name__)


WIN10_CMD_TABLE = ({"Command": "cd",
                    "Return": {"remote":
                        {0: 'C:\\Users\\STE\\Projects\\AutoRAID'},
                        "local": {0: '/home/pi'}}
                    },
                   {"Command": "ver",
                   "Return": {"remote": {0: '',
                            1: 'Microsoft Windows [Version 10.0.19045.4780]'},
                            "local": {0: '6.1.21-v8+'}}
                    })


class TestWin10Interface(object):
    @pytest.mark.skip(reason="Obsoleted")
    @pytest.mark.parametrize("win_cmd", WIN10_CMD_TABLE)
    def test_command_line(self, my_win10, win_cmd):
        list_executed = my_win10.command_line(win_cmd["Command"])
        logger.info(f'Return = {list_executed}')
        # logger.debug(f'Command Type = {type(list_executed)}')
        assert list_executed == win_cmd["Return"][my_win10.mode]