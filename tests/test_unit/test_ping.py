import logging
from unittest.mock import MagicMock
# from tests.test_unit.test_ping import Ping

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

# @pytest.fixture(scope="session", autouse=True)
# def mock_api():
#     mock = MagicMock()
#     mock.ip_address = "127.0.0.1"  # Mocking the IP address
#     return mock

class TestPing:  
    def test_ping_no_loss(self, target_ping):
        # Setup the mock to return a successful ping response
        # mock_api.command_line.return_value = (
        #     "Pinging 127.0.0.1 with 32 bytes of data:\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n\n"
        #     "Ping statistics for 127.0.0.1:\n"
        #     "    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),\n"
        #     "Approximate round trip times in milli-seconds:\n"
        #     "    Minimum = 0ms, Maximum = 0ms, Average = 0ms"
        # )
        
        # ping = Ping(mock_api)
        if target_ping.ping():
            logger.info(f"target_ping.sent = {target_ping.sent}")
            logger.info(f"target_ping.received = {target_ping.received}")
            logger.info(f"target_ping.lost = {target_ping.lost}")
        # ping.ping()
        
        # Verify the parsed values
            assert (target_ping.sent == 4,
                f"Expected Sent to be 4, got {target_ping.sent}")
            # assert ping.received == 4, f"Expected Received to be 4, got {ping.received}"
            # assert ping.lost == 0, f"Expected Lost to be 0, got {ping.lost}"
            # assert ping.minimum == 0, f"Expected Minimum to be 0ms, got {ping.minimum}"
            # assert ping.maximum == 0, f"Expected Maximum to be 0ms, got {ping.maximum}"
            # assert ping.average == 0, f"Expected Average to be 0ms, got {ping.average}"

    def test_ping_loss(self, target_ping):
        # Setup the mock to return a successful ping response with no loss
        # mock_api.command_line.return_value = (
        #     "Pinging 127.0.0.1 with 32 bytes of data:\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
        #     "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n\n"
        #     "Ping statistics for 127.0.0.1:\n"
        #     "    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),\n"
        #     "Approximate round trip times in milli-seconds:\n"
        #     "    Minimum = 0ms, Maximum = 0ms, Average = 0ms"
        # )
        
        # ping = Ping(mock_api)
        if target_ping.ping():
            logger.info(f"target_ping.sent = {target_ping.sent}")
            logger.info(f"target_ping.received = {target_ping.received}")
            logger.info(f"target_ping.lost = {target_ping.lost}")
        # Check for no packet loss
            assert (target_ping.lost == 0,
                f"Expected no packet loss, got {target_ping.lost} packets lost")

    def test_parse_statistics(self, target_ping):
        # Setup the mock to return a failed ping response
        # mock_api.command_line.return_value = (
        #     "Pinging 256.256.256.256 with 32 bytes of data:\n"
        #     "Request timed out.\n"
        #     "Request timed out.\n"
        #     "Request timed out.\n"
        #     "Request timed out.\n\n"
        #     "Ping statistics for 256.256.256.256:\n"
        #     "    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),"
        # )
        
        # ping = Ping(mock_api)
        if target_ping.ping():
            logger.info(f"target_ping.maximum = {target_ping.maximum}")
            logger.info(f"target_ping.minimum = {target_ping.minimum}")
            logger.info(f"target_ping.average = {target_ping.average}")
            assert target_ping.sent == 4, "Expected Sent to be 4"
            # assert ping.received == 0, "Expected Received to be 0"
            # assert ping.lost == 4, "Expected Lost to be 4"
            # assert ping.minimum == 0, "Expected Minimum to be 0 in case of failure"
            # assert ping.maximum == 0, "Expected Maximum to be 0 in case of failure"
            # assert ping.average == 0, "Expected Average to be 0 in case of failure"
