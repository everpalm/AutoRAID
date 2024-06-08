# Contents of test_application_interface.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
from win10_interface import Win10Interface as win10

''' Set up logger '''
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


WIN10_CMD_TABLE = ({"Command": "cd",
                    "Return": {"remote":
                        {0: 'C:\\Users\\Administrator\\Documents\\Projects\\AutoRAID'},
                        "local": {0: '/home/pi'}}
                    },
                   {"Command": "ver",
                   "Return": {"remote": {0: '',
                            1: 'Microsoft Windows [Version 10.0.19045.4412]'},
                            "local": {0: '6.1.21-v8+'}}
                    })


class TestWin10Interface(object):
    @pytest.fixture(scope="session", autouse=True)
    def my_win10(self, cmdopt):
        print('\n\033[32m================ Setup Win10 ===============\033[0m')
        return win10(cmdopt.get('mode'), cmdopt.get('if_name'),
        cmdopt.get('config_file'))
    
    @pytest.mark.parametrize("win_cmd", WIN10_CMD_TABLE)
    def test_command_line(self, my_win10, win_cmd):
        list_executed = my_win10.command_line(win_cmd["Command"])
        logger.debug("my_app.command_line = %s, type %s", list_executed,
                     type(list_executed))
        assert list_executed == win_cmd["Return"][my_win10.mode]