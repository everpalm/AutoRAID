import logging
import pytest

logger = logging.getLogger(__name__)

IO_EVENTS = (
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
    @pytest.mark.parametrize('io_events', IO_EVENTS)
    def test_find_error(self, win_event, io_events):
        output = win_event.find_error(io_events["LogName"],
                                    io_events["Event ID"],
                                    io_events["Pattern"])
        logger.debug(f'output = {output}')
        assert output == False


