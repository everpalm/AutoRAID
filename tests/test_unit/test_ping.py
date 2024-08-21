# Contents of test_ping.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
from unittest.mock import MagicMock
from unit.ping import LinuxPing
from unit.ping import WindowsPing

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)


class TestPing(object):
    def test_linux_ping(self, mock_api):
        ping_instance = LinuxPing(mock_api)
        mock_api.command_line.return_value = {
            0: 'PING 192.168.0.128 (192.168.0.128) 56(84) bytes of data.',
            1: '64 bytes from 192.168.0.128: icmp_seq=1 ttl=128 time=0.300 ms',
            6: '4 packets transmitted, 4 received, 0% packet loss, time 85ms',
            7: 'rtt min/avg/max/mdev = 0.300/0.337/0.351/0.021 ms'
        }
        
        result = ping_instance.ping()

        logger.info(f'ping_instance.sent = {ping_instance.sent}')
        logger.info(f'ping_instance.received = {ping_instance.received}')
        logger.info(f'ping_instance.lost = {ping_instance.lost}')
        logger.info(f'ping_instance.minimum = {ping_instance.minimum}')
        logger.info(f'ping_instance.maximum = {ping_instance.maximum}')
        logger.info(f'ping_instance.average = {ping_instance.average}')
        logger.info(f'ping_instance.deviation = {ping_instance.deviation}')

        assert result == True
        assert ping_instance.sent == 4
        assert ping_instance.received == 4
        assert ping_instance.lost == 0
        assert ping_instance.minimum == 0.300
        assert ping_instance.average == 0.337
        assert ping_instance.maximum == 0.351
        assert ping_instance.deviation == 0.021

    def test_linux_ping_loss(self, mock_api):
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

        logger.info(f'ping_instance.sent = {ping_instance.sent}')
        logger.info(f'ping_instance.received = {ping_instance.received}')
        logger.info(f'ping_instance.lost = {ping_instance.lost}')
        logger.info(f'ping_instance.minimum = {ping_instance.minimum}')
        logger.info(f'ping_instance.maximum = {ping_instance.maximum}')
        logger.info(f'ping_instance.average = {ping_instance.average}')
        logger.info(f'ping_instance.deviation = {ping_instance.deviation}')
        
        # 检查返回值是否为False，表示ping失败
        assert result == False
        # 验证解析结果
        assert ping_instance.sent == 4
        assert ping_instance.received == 0
        assert ping_instance.lost == 4
        assert ping_instance.minimum == 0
        assert ping_instance.average == 0
        assert ping_instance.maximum == 0
        assert ping_instance.deviation == 0

    def test_windows_ping(self, mock_api):
        ping_instance = WindowsPing(mock_api)
        mock_api.command_line.return_value = {
            0: 'Pinging 192.168.0.128 with 32 bytes of data:',
            1: 'Reply from 192.168.0.128: bytes=32 time=1ms TTL=128',
            6: 'Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),',
            7: 'Minimum = 1ms, Maximum = 1ms, Average = 1ms'
        }
        
        result = ping_instance.ping()

        logger.info(f'ping_instance.sent = {ping_instance.sent}')
        logger.info(f'ping_instance.received = {ping_instance.received}')
        logger.info(f'ping_instance.lost = {ping_instance.lost}')
        logger.info(f'ping_instance.minimum = {ping_instance.minimum}')
        logger.info(f'ping_instance.maximum = {ping_instance.maximum}')
        logger.info(f'ping_instance.average = {ping_instance.average}')

        assert result == True
        assert ping_instance.sent == 4
        assert ping_instance.received == 4
        assert ping_instance.lost == 0
        assert ping_instance.minimum == 1
        assert ping_instance.average == 1
        assert ping_instance.maximum == 1

    def test_windows_ping_loss(self, mock_api):
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

        logger.info(f'ping_instance.sent = {ping_instance.sent}')
        logger.info(f'ping_instance.received = {ping_instance.received}')
        logger.info(f'ping_instance.lost = {ping_instance.lost}')
        logger.info(f'ping_instance.minimum = {ping_instance.minimum}')
        logger.info(f'ping_instance.maximum = {ping_instance.maximum}')
        logger.info(f'ping_instance.average = {ping_instance.average}')

        # 检查返回值是否为False，表示ping失败
        assert result == False
        # 验证解析结果
        assert ping_instance.sent == 4
        assert ping_instance.received == 0
        assert ping_instance.lost == 4
        assert ping_instance.minimum == 0
        assert ping_instance.average == 0
        assert ping_instance.maximum == 0
