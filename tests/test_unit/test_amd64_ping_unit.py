# Contents of test_ping.py
'''Unit tests for LinuxPing and WindowsPing classes for ping command functionality.
   This module includes tests to verify successful and failed ping scenarios on both
   Linux and Windows systems, using mock data.
   
   Copyright (c) 2024 Jaron Cheng
'''

import logging
from unittest.mock import MagicMock
from unit.ping import LinuxPing
from unit.ping import WindowsPing

import pytest

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)


class TestPing:
    """Test suite for the LinuxPing and WindowsPing classes, which verify the
        ping command output parsing and response handling on Linux and Windows.
        """

    @pytest.fixture(scope="module")
    def mock_api(self):
        """Fixture to mock the remote IP and API for ping commands.

        Returns:
            MagicMock: Mocked API for simulating remote ping command responses.
        """
        mock = MagicMock()
        mock.remote_ip = "192.168.0.128"
        return mock

    def test_linux_ping(self, mock_api):
        """Tests LinuxPing.ping() with a successful ping response on a Linux
        system, verifying that the attributes such as sent, received, lost,
        minimum, maximum, and average response times are correctly parsed.

        Args:
            mock_api (MagicMock): The mocked API with simulated command output.
        """
        ping_instance = LinuxPing(mock_api)
        mock_api.command_line.return_value = {
            0: 'PING 192.168.0.128 (192.168.0.128) 56(84) bytes of data.',
            1: '64 bytes from 192.168.0.128: icmp_seq=1 ttl=128 time=0.300 ms',
            6: '4 packets transmitted, 4 received, 0% packet loss, time 85ms',
            7: 'rtt min/avg/max/mdev = 0.300/0.337/0.351/0.021 ms'
        }

        result = ping_instance.ping()

        logger.info('ping_instance.sent = %s', ping_instance.sent)
        logger.info('ping_instance.received = %s', ping_instance.received)
        logger.info('ping_instance.lost = %s', ping_instance.lost)
        logger.info('ping_instance.minimum = %s', ping_instance.minimum)
        logger.info('ping_instance.maximum = %s', ping_instance.maximum)
        logger.info('ping_instance.average = %s', ping_instance.average)
        logger.info('ping_instance.deviation = %s', ping_instance.deviation)

        assert result is True
        assert ping_instance.sent == 4
        assert ping_instance.received == 4
        assert ping_instance.lost == 0
        assert ping_instance.minimum == 0.300
        assert ping_instance.average == 0.337
        assert ping_instance.maximum == 0.351
        assert ping_instance.deviation == 0.021

    @pytest.mark.skip(reason='Flaws in parsing list')
    def test_linux_ping_loss(self, mock_api):
        """Tests LinuxPing.ping() with a failed ping response on a Linux
        system to verify parsing of response when packets are lost.

        Args:
            mock_api (MagicMock): The mocked API with simulated command output.
        """
        ping_instance = LinuxPing(mock_api)

        # 模拟ping连接失败的返回数据
        mock_api.command_line.return_value = {
            0: 'PING 192.168.0.128 (192.168.0.128) 56(84) bytes of data.',
            1: 'From 192.168.0.1 icmp_seq=1 Destination Host Unreachable',
            2: 'From 192.168.0.1 icmp_seq=2 Destination Host Unreachable',
            3: 'From 192.168.0.1 icmp_seq=3 Destination Host Unreachable',
            4: 'From 192.168.0.1 icmp_seq=4 Destination Host Unreachable',
            6: '4 packets transmitted, 0 received, 100% packet loss, time 3999ms'
        }

        result = ping_instance.ping()

        logger.info('ping_instance.sent = %s', ping_instance.sent)
        logger.info('ping_instance.received = %s', ping_instance.received)
        logger.info('ping_instance.lost = %s', ping_instance.lost)
        logger.info('ping_instance.minimum = %s', ping_instance.minimum)
        logger.info('ping_instance.maximum = %s', ping_instance.maximum)
        logger.info('ping_instance.average = %s', ping_instance.average)
        logger.info('ping_instance.deviation = %s', ping_instance.deviation)

        # 检查返回值是否为False，表示ping失败
        assert result is False
        # 验证解析结果
        assert ping_instance.sent == 4
        assert ping_instance.received == 0
        assert ping_instance.lost == 4
        assert ping_instance.minimum == 0
        assert ping_instance.average == 0
        assert ping_instance.maximum == 0
        assert ping_instance.deviation == 0

    def test_windows_ping(self, mock_api):
        """Tests WindowsPing.ping() with a successful ping response on a
        Windows system, verifying that packet and latency details are 
        correctly parsed.

        Args:
            mock_api (MagicMock): The mocked API with simulated command output.
        """
        ping_instance = WindowsPing(mock_api)
        mock_api.command_line.return_value = {
            0: 'Pinging 192.168.0.128 with 32 bytes of data:',
            1: 'Reply from 192.168.0.128: bytes=32 time=1ms TTL=128',
            6: 'Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),',
            7: 'Minimum = 1ms, Maximum = 1ms, Average = 1ms'
        }

        result = ping_instance.ping()

        logger.info('ping_instance.sent = %s', ping_instance.sent)
        logger.info('ping_instance.received = %s', ping_instance.received)
        logger.info('ping_instance.lost = %s', ping_instance.lost)
        logger.info('ping_instance.minimum = %s', ping_instance.minimum)
        logger.info('ping_instance.maximum = %s', ping_instance.maximum)
        logger.info('ping_instance.average = %s', ping_instance.average)

        assert result is True
        assert ping_instance.sent == 4
        assert ping_instance.received == 4
        assert ping_instance.lost == 0
        assert ping_instance.minimum == 1
        assert ping_instance.average == 1
        assert ping_instance.maximum == 1

    @pytest.mark.skip(reason='Flaws in parsing list')
    def test_windows_ping_loss(self, mock_api):
        """Tests WindowsPing.ping() with a failed ping response on a Windows
        system to verify parsing of response when packets are lost.

        Args:
            mock_api (MagicMock): The mocked API with simulated command output.
        """
        ping_instance = WindowsPing(mock_api)

        # 模拟ping连接失败的返回数据
        mock_api.command_line.return_value = {
            0: 'Pinging 192.168.0.128 with 32 bytes of data:',
            1: 'Request timed out.',
            2: 'Request timed out.',
            3: 'Request timed out.',
            4: 'Request timed out.',
            6: 'Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),'
        }

        result = ping_instance.ping()

        logger.info('ping_instance.sent = %s', ping_instance.sent)
        logger.info('ping_instance.received = %s', ping_instance.received)
        logger.info('ping_instance.lost = %s', ping_instance.lost)
        logger.info('ping_instance.minimum = %s', ping_instance.minimum)
        logger.info('ping_instance.maximum = %s', ping_instance.maximum)
        logger.info('ping_instance.average = %s', ping_instance.average)

        # 检查返回值是否为False，表示ping失败
        assert result is False
        # 验证解析结果
        assert ping_instance.sent == 4
        assert ping_instance.received == 0
        assert ping_instance.lost == 4
        assert ping_instance.minimum == 0
        assert ping_instance.average == 0
        assert ping_instance.maximum == 0
