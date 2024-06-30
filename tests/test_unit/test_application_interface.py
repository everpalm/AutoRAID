# Contents of test_application_interface.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
# from unit.application_interface import ApplicationInterface as api

''' Set up logger '''
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

LINUX_CMD_TABLE = ({"Command": "pwd",
                    "Return": {"remote": {0: '/home/test/FW_Generic'},
                               "local": {0: '/home/pi'}}
                    },
                   {"Command": "uname -r",
                    "Return": {"remote": {0: '4.10.0-40-generic'},
                               "local": {0: '6.1.21-v8+'}}
                    })

class TestApplicationInterface(object):
    # @pytest.fixture(scope="session", autouse=True)
    # def my_app(self, cmdopt):
    #     logger.info('====================Setup API====================')
    #     return api(cmdopt.get('mode'),
    #                cmdopt.get('if_name'),
    #                cmdopt.get('config_file'))
    @pytest.mark.skip(reason="Current SUT is Windows")
    @pytest.mark.parametrize("linux_cmd", LINUX_CMD_TABLE)
    def test_command_line(self, my_app, linux_cmd):
        list_executed = my_app.command_line(linux_cmd["Command"])
        logger.debug("my_app.command_line = %s, type %s",
                    list_executed, type(list_executed))
        assert list_executed == linux_cmd["Return"][my_app.mode]