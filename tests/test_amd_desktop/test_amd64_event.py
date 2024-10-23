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
    }
)

# class TestAMD64Event:
#     @pytest.mark.parametrize('io_events', IO_EVENTS)
#     def test_find_error(self, win_event, io_events):
#     # def test_find_error(self, win_event):
#     #     for io_event in IO_EVENTS:
#     #         log_name = io_event["LogName"]
#     #         event_id = io_event["Event ID"]
#     #         pattern = io_event["Pattern"]
#         output = win_event.find_error(io_events["LogName"],
#                                     io_events["Event ID"],
#                                     io_events["Pattern"])
#             # output = win_event.find_error(log_name, event_id, pattern)
#         logger.debug(f'output = {output}')
#         assert output == False


