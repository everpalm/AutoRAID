import logging
import pytest

logger = logging.getLogger(__name__)
# with open(f'config/amd64_event.json', 'r', encoding='utf-8') as f:
#     MY_EVENTS = [json.load(f)]
log_name = 'System'
event_id = 157
pattern = r'Disk (\d+) has been surprise removed.'
MY_EVENTS = (
    {
        "LogName": "System",
        "Event ID": 157,
        "Pattern": r'Disk (\d+) has been surprise removed.'
    },
    {
        "LogName": "System",
        "Event ID": 51,
        "Pattern": r'An error was detected on device (\\\w+\\\w+\\\w+)'
    }
)

class TestAMD64Event:
    @pytest.mark.parametrize('my_events', MY_EVENTS)
    def test_find_error_event(self, win_event, my_events):
        logger.debug(f'win_event.config_file = {win_event.config_file}')
        # output = win_event.get_stornvme()
        # output = win_event.find_error_event(log_name, event_id, pattern)
        output = win_event.find_error_event(my_events["LogName"], my_events["Event ID"], my_events["Pattern"])
        print(f'output = {output}')
        # print(f'my_events = {my_events}')


