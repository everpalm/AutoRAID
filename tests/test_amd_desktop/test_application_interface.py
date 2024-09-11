# Contents of test_application_interface.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
# from unit.application_interface import ApplicationInterface as api

''' Set up logger '''
# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

WINDOWS_CMD_TABLE = ({
                        "Command": "cd",
                        "Return": {
                            "remote": {0: "C:\\Users\\STE\\Projects\\AutoRAID"}
                        }
                    },
                   {
                       "Command": "ver",
                        "Return": {
                            "remote": {
                                0: '',
                                1: 'Microsoft Windows [Version 10.0.19045.4780]'
                            }
                        }
                    })

class TestApplicationInterface(object):
    
    @pytest.mark.parametrize("windows_cmd", WINDOWS_CMD_TABLE)
    def test_command_line(self, my_app, windows_cmd):
        list_executed = my_app.command_line(windows_cmd["Command"])
        logger.debug("my_app.command_line = %s, type %s",
                    list_executed, type(list_executed))
        assert list_executed == windows_cmd["Return"][my_app.mode]