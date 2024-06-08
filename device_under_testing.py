# Contents of device_under_testing.py
'''Copyright (c) 2024 Jaron Cheng'''

import logging
import json
from system_under_testing import SystemUnderTasting as sut

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def export_json_file(callback):
    def dump_json_file(*args, **kwargs):
        result = callback(*args, **kwargs)
        logger.debug("Dictionary to be exported = %s", result)
        json_data = json.dumps(result)
        with open("MY_DEVICE_INFO.json", "w") as file:
            try:
                rtn = file.write(json_data)
            except IOError:
                raise Exception("Write file failed, error code = %s", rtn)
    return dump_json_file


class DeviceUnderTesting(sut):
    ''' Device Under Testing

        Describe the behaviors of PCIe Device

        Attributes:
            manufacturer: Any
            vendor_id: Any
            serial_no: default value is 1234-5678-abcd-ef
    '''
    def __init__(self):
        super().__init__(str_manufacturer='Any')
        self.vendor_id, self.serial_no = self.identify_device().values()

    def identify_device(self):
        __dict_return = self.command_line(f'./my_app --dev-id {self.bdf} ident')
        str_vendor_id = __dict_return.get(7).split(' ')[-1]
        logger.info('str_vendor_id = %s', str_vendor_id)
        str_serial_no = __dict_return.get(8).split(' ')[-1]
        logger.info('str_serial_no = %s', str_serial_no)
        return {"Vendor ID": str_vendor_id, "Serial Number": str_serial_no}
    
    @export_json_file
    def get_pcie_json(self):
        return self.identify_device()
    

# class Lionperf(DeviceUnderTesting):
#     def __init__(self, dict_options):
#         super().__init__()
#         self.enable_console_log, self.disable_msix, self.sim_mode = dict_options.values()
    
#     def set_options(self):
#         a = self.enable_console_log
#         b = self.disable_msix
#         c = self.sim_mode
#         logger.debug("str_command_line = %s", a)
#         return a, b, c
    
