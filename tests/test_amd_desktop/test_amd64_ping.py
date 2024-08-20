import logging

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TestAMD64Ping(object):
    def test_parse_statistics(self, target_ping):
        if target_ping.ping():
            logger.info(f"target_ping.maximum = {target_ping.maximum}")
            logger.info(f"target_ping.minimum = {target_ping.minimum}")
            logger.info(f"target_ping.average = {target_ping.average}")

            assert target_ping.maximum == 0, f"Expected Minimum to be 0ms, \
                got {target_ping.maximum}"
            assert target_ping.minimum == 0, f"Expected Maximum to be 0ms, \
                got {target_ping.minimum}"
            assert target_ping.average == 0, f"Expected Average to be 0ms, \
                got {target_ping.average}"

    def test_ping_no_loss(self, target_ping):
        if target_ping.ping():
            # Verify the parsed values
            logger.info(f"target_ping.sent = {target_ping.sent}")
            logger.info(f"target_ping.received = {target_ping.received}")
            logger.info(f"target_ping.lost = {target_ping.lost}")
        
            assert target_ping.sent == 4
            assert target_ping.received == 4
            assert target_ping.lost == 0

    #     # Setup the mock to return a successful ping response with no loss
    #     target_ping.command_line.return_value = (
    #         "Pinging 127.0.0.1 with 32 bytes of data:\n"
    #         "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
    #         "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
    #         "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
    #         "Reply from 127.0.0.1: bytes=32 time<1ms TTL=128\n\n"
    #         "Ping statistics for 127.0.0.1:\n"
    #         "    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),\n"
    #         "Approximate round trip times in milli-seconds:\n"
    #         "    Minimum = 0ms, Maximum = 0ms, Average = 0ms"
    #     )
        
    #     ping = AMD64Ping(mock_api)
    #     ping.ping()
        
    #     # Check for no packet loss
    #     assert ping.lost == 0, f"Expected no packet loss, got {ping.lost} packets lost"

    # def test_ping_failure_statistics(self, mock_api):
    #     # Setup the mock to return a failed ping response
    #     mock_api.command_line.return_value = (
    #         "Pinging 256.256.256.256 with 32 bytes of data:\n"
    #         "Request timed out.\n"
    #         "Request timed out.\n"
    #         "Request timed out.\n"
    #         "Request timed out.\n\n"
    #         "Ping statistics for 256.256.256.256:\n"
    #         "    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),"
    #     )
        
    #     ping = AMD64Ping(mock_api)
    #     ping.ping()
        
    #     assert ping.sent == 4, "Expected Sent to be 4"
    #     assert ping.received == 0, "Expected Received to be 0"
    #     assert ping.lost == 4, "Expected Lost to be 4"
    #     assert ping.minimum == 0, "Expected Minimum to be 0 in case of failure"
    #     assert ping.maximum == 0, "Expected Maximum to be 0 in case of failure"
    #     assert ping.average == 0, "Expected Average to be 0 in case of failure"
