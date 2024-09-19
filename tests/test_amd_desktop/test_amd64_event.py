import logging
import pytest

logger = logging.getLogger(__name__)

MY_EVENTS = (
    {
        "LogName": "System",
        "Event ID": 157,
        "Pattern": r'Disk (\d+) has been surprise removed.'
    },
    {
        "LogName": "System",
        "Event ID": 51,
        "Pattern": r'An error was detected on device (\\\w+\\\w+\.+)'
        # "Pattern": r'Warning disk (\d+)'
    }
)

class TestAMD64Event:
    @pytest.mark.parametrize('my_events', MY_EVENTS)
    def test_find_error_event(self, win_event, my_events):
        logger.debug(f'win_event.config_file = {win_event.config_file}')
        output = win_event.find_error_event(my_events["LogName"],
                                            my_events["Event ID"],
                                            my_events["Pattern"])
        print(f'output = {output}')



