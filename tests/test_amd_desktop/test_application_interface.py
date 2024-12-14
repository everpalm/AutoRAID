# Contents of test_application_interface.py
'''Unit tests for the ApplicationInterface class, which includes testing the 
   execution of Windows commands to verify system responses and configurations
   
   Copyright (c) 2024 Jaron Cheng
'''

import logging
import pytest

# Set up logger
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
                                1: 'Microsoft Windows [Version 10.0.19045.5247]'
                            }
                        }
                    })

class TestApplicationInterface:
    '''This is a docstring'''
    @pytest.mark.parametrize("windows_cmd", WINDOWS_CMD_TABLE)
    def test_command_line(self, my_app, windows_cmd):
        """Tests the command_line method of the ApplicationInterface class
        by sending Windows commands and comparing the output with the expected 
        results from the WINDOWS_CMD_TABLE.
        
        Args:
            my_app (ApplicationInterface): The ApplicationInterface instance used 
                for testing, typically provided as a fixture.
            windows_cmd (dict): A dictionary representing a command and expected
                return value for the test case.
        
        Assertions:
            - Checks that the output from executing the command matches the
            expected return value in WINDOWS_CMD_TABLE.
        """
        list_executed = my_app.command_line(windows_cmd["Command"])
        logger.debug("my_app.command_line = %s, type %s",
                    list_executed, type(list_executed))
        assert list_executed == windows_cmd["Return"][my_app.mode]
