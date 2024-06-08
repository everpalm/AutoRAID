# Contents of test_device_under_testing.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import pytest
import json
from device_under_testing import DeviceUnderTesting as dut


''' Set up logger '''
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

LION_PCIE_INFO = [{'Manufacturer':'Microsoft', 'SDID':'c003', "BDF": '01:00.0', "Vendor ID": '1414', "Serial Number": '1234-5678-abcd-ef'}]
LIONAPP_OPTIONS = {'Enable Console Logs': '-c',
                    'Disable MSIX': '--disable-msix',
                    'Simulated Mode': '--sim',
                    }
@pytest.fixture(scope="session", autouse=True)
def setup_dut():
    logger.info('====================Setup DUT====================')
    global obj_lion_dut
    obj_lion_dut = dut()
    logger.debug('obj_lion_dut.sdid = %s', obj_lion_dut.sdid)
    logger.debug('obj_lion_dut.bdf = %s', obj_lion_dut.bdf)
    # yield obj_lion_sut.bdf
    # logger.info('Teardown: obj_lion_sut.ip = %s', obj_lion_sut.ip)
    
class TestDeviceUnderTesting(object):
    @pytest.mark.skip(reason="Dummy test")
    @pytest.mark.parametrize('lion_pci_info', LION_PCIE_INFO)
    def test_identify_device(self, lion_pci_info):
        logger.debug("lion_pci_info = %s", lion_pci_info)
        assert lion_pci_info["Vendor ID"] == obj_lion_dut.vendor_id
        assert lion_pci_info["Serial Number"] == obj_lion_dut.serial_no

    @pytest.mark.skip(reason="Dummy test")
    def test_get_pcie_json(self):
        target_pci_info = obj_lion_dut.get_pcie_json()
        logger.debug("Dummy test: target_pci_info = %s", target_pci_info)
        assert target_pci_info == None



# if __name__ == '__main__':
    # pytest.main(['test_system_under_testing.py', '-s', '-v', '-x'])

