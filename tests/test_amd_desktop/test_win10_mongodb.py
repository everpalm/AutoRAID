# Contents of test_win10_mongodb.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import pytest

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

WMDB_ATTR = [{
    "Log Path": '/home/pi/uart.log',
    "Report Path": ".report.json"
}]


@pytest.mark.parametrize("wmdb_attr", WMDB_ATTR)
class TestWin10MongoDB(object):
     def test_write_log_and_report(self, my_wmdb, wmdb_attr):
         _ = my_wmdb.write_log_and_report(
            wmdb_attr["Log Path"],
            wmdb_attr["Report Path"])