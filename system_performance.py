# Contents of system_performance.py
'''Copyright (c) 2024 Jaron Cheng'''
import logging
import os
import pandas as pd
# from system_under_testing import SystemUnderTasting as sut

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SystemPerformance(object):
    ''' System Performance

        Performance of the system that are not included in the DUT behavior

        Attributes:
            os: Operation System
            manufacturer: Any
            bdf: Bus-Device-Function in the format of xx:yy.zz
            sdid: The Sub-device ID of PCIe, confirm SDID of PCI device in advance
    '''
    # def __init__(self, str_file_path, str_group_key, str_key, str_group):
    def __init__(self, str_file_path: str, str_group_key: str):
        self.file_path = str_file_path
        self.group_key = str_group_key
        # self.group = str_group
        # self.key = str_key

    def groupby_io_mean(self, str_key: str, str_group: str) -> str:
        ''' Groupby IO data and return its mean value
            Args: Group key, data key, and data value
            Returns: data mean
            Raises:FileNotFoundError
        '''
        if os.path.exists(self.file_path):
            df_perf = pd.read_json(self.file_path, orient='records',
                                   lines=True)
            df_grouped = df_perf.groupby(self.group_key).mean(
                numeric_only=True)
            logger.info("===Groupby===")
            print(df_grouped)
            # print(df_grouped.corr())
            # print(df_grouped.corr().columns)
            # print(df_grouped.corr().index)
            # print(df_grouped.corr().loc['IOPS']['BW'])
            logger.info("===Correlation===")
            print(df_grouped.corr().loc[str_group])
            # print(df_grouped.corr().loc[str_group]['BW'])

        else:
            raise FileNotFoundError("File not found")
        return df_grouped.loc[str_key][str_group]

    # def kill_process(self, str_process):
    #     ''' Kill process
    #         Args:
    #         Returns:
    #         Raises:
    #     '''
    #     try:
    #         _dict_return = self.command_line(f'killall {str_process}')
    #         logger.debug('kill_process = %s', _dict_return)
    #     except:
    #         pass
    #     finally:
    #         return _dict_return
