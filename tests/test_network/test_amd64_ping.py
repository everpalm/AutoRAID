# Contents of tests/test_network/test_amd64_ping.py
'''Unit tests for the AMD64Ping functionality, ensuring that network
   connectivity can be verified and that round-trip times (RTT) are correctly
   measured and reported.

   Copyright (c) 2024 Jaron Cheng
'''
import logging
import pytest

logger = logging.getLogger(__name__)


class TestAMD64Ping:
    """Test suite for AMD64Ping class, verifying ping response metrics and
    overall functionality.

    Attributes:
        target_ping (AMD64Ping): Instance used to perform ping operations,
        measuring sent, received, and lost packets, as well as latency metrics.
    """
    @pytest.mark.flaky(reruns=3, reruns_delay=10)
    # @pytest.mark.xfail(reason="Cannot be used with flaky")
    def test_ping_ok(self, target_ping):
        """Tests the `ping` method of the AMD64Ping class for successful
        connectivity and RTT metrics.

        Ensures that packets are sent, received, and that the round-trip
        times (RTT) are within reasonable ranges. If the ping fails, retries
        up to three times with a 10-second delay.

        Args:
            target_ping (AMD64Ping): Mocked instance of AMD64Ping for
            performing the ping test.

        Assertions:
            - result: Ping should succeed.
            - target_ping.sent: Packets sent should be greater than 0.
            - target_ping.received: Packets received should be greater than 0.
            - target_ping.lost: Packets lost should be 0 or greater.
            - target_ping.minimum: Minimum RTT should be 0 or greater.
            - target_ping.average: Average RTT should be 0 or greater.
            - target_ping.maximum: Maximum RTT should be 0 or greater.
            - target_ping.deviation: Deviation of RTT should be 0 or greater.
        """
        result = target_ping.ping()

        logger.info('target_ping.sent = %s', target_ping.sent)
        logger.info('target_ping.received = %s', target_ping.received)
        logger.info('target_ping.lost = %s', target_ping.lost)
        logger.info('target_ping.minimum = %s', target_ping.minimum)
        logger.info('target_ping.maximum = %s', target_ping.maximum)
        logger.info('target_ping.average = %s', target_ping.average)
        logger.info('target_ping.deviation = %s', target_ping.deviation)

        assert result is True, "Ping should succeed"
        assert target_ping.sent > 0, "Packets sent should be greater than 0"
        assert target_ping.received > 0, ("Packets received should be greater"
                                          "than 0")
        assert target_ping.lost >= 0, "Packets lost should be 0 or greater"
        assert target_ping.minimum >= 0, "Minimum RTT should be 0 or greater"
        assert target_ping.average >= 0, "Average RTT should be 0 or greater"
        assert target_ping.maximum >= 0, "Maximum RTT should be 0 or greater"
        assert target_ping.deviation >= 0, ("Deviation RTT should be 0 or"
                                            " greater")
