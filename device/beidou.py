# Contents of device/1b4b_2241.py
'''Copyright (c) 2025 Jaron Cheng'''
# import json
import logging
import re
from abc import ABC
from abc import abstractmethod
from commandline.mnv_cli import BaseCLI
# from dataclasses import dataclass
# from dataclasses import field
from interface.application import BaseInterface
from interface.application import NVMeController
from interface.application import RootComplex
from interface.application import EndPoint
# from typing import List
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


# @dataclass
# class RootComplex:
#     id: int
#     link_width: str
#     pcie_speed: str


# @dataclass
# class EndPoint:
#     id: int
#     link_width: str
#     pcie_speed: str


# @dataclass
# class NVMeController:
#     '''This is a docstring'''
#     bus_device_func: str
#     device: str
#     slot_id: str
#     firmware_version: str
#     vid: str
#     svid: str
#     did: str
#     sdid: str
#     revision_id: str
#     port_count: int
#     max_pd_of_per_vd: int
#     max_vd: int
#     max_pd: int
#     max_ns_of_per_vd: int
#     max_ns: int
#     supported_raid_mode: List[str]
#     cache: str
#     supported_bga_features: List[str]
#     support_stripe_size: List[str]
#     supported_features: List[str]
#     root_complexes: List[RootComplex] = field(default_factory=list)
#     end_points: List[EndPoint] = field(default_factory=list)


class BaseDevice(ABC):
    '''This is a docstring'''
    def __init__(self, command: BaseCLI):
        '''This is a docstring'''
        self.cmd = command
        self.controller_info = self.get_controller_info()

    @abstractmethod
    def get_controller_info(self) -> str:
        '''docstring'''
        pass


class Changhua(BaseDevice):
    def get_controller_info(self) -> str:
        try:
            output = self.cmd.interpret('info -o hba')
            logger.debug('output = %s', output)
            data = {}
            root_complexes = []
            end_points = []
            current_section = None

            if isinstance(output, list):
                lines = output
            elif isinstance(output, str):
                lines = output.splitlines()
            else:
                raise TypeError("Invalid output type, expected str or list")

            for line in lines:
                match = re.match(r"(.*?):\s+(.*)", line)
                if match:
                    key, value = match.groups()
                    key = re.sub(r'[^a-zA-Z0-9_]', '_', key.lower())

                    if key.startswith("root_complex"):
                        root_id = int(value)
                        root_complexes.append(RootComplex(
                            id=root_id,
                            link_width="",
                            pcie_speed=""
                        ))
                        current_section = "root_complex"
                    elif key.startswith("end_point"):
                        end_id = int(value)
                        end_points.append(EndPoint(id=end_id, link_width="",
                                                   pcie_speed=""))
                        current_section = "end_point"
                    elif key == "link_width":
                        if current_section == \
                                "root_complex" and root_complexes:
                            root_complexes[-1].link_width = value
                        elif current_section == "end_point" and end_points:
                            end_points[-1].link_width = value
                    elif key == "pcie_speed":
                        if current_section == "root_complex" and \
                                root_complexes:
                            root_complexes[-1].pcie_speed = value
                        elif current_section == "end_point" and end_points:
                            end_points[-1].pcie_speed = value
                    else:
                        data[key] = value

            # Convert specific values to correct types
            int_fields = ["port_count", "max_pd_of_per_vd", "max_vd", "max_pd",
                          "max_ns_of_per_vd", "max_ns"]
            for int_field in int_fields:
                data[int_field] = int(data.get(int_field, 0))

            list_fields = ["supported_raid_mode", "supported_bga_features",
                           "support_stripe_size", "supported_features"]
            for list_field in list_fields:
                data[list_field] = data.get(list_field, "").split()

            return NVMeController(
                bus_device_func=data.get("bus_device_fun", ""),
                device=data.get("device", ""),
                slot_id=data.get("slot_id", ""),
                firmware_version=data.get("firmware_version", ""),
                vid=data.get("vid", ""),
                svid=data.get("svid", ""),
                did=data.get("did", ""),
                sdid=data.get("sdid", ""),
                revision_id=data.get("revisionid", ""),
                port_count=data["port_count"],
                max_pd_of_per_vd=data["max_pd_of_per_vd"],
                max_vd=data["max_vd"],
                max_pd=data["max_pd"],
                max_ns_of_per_vd=data["max_ns_of_per_vd"],
                max_ns=data["max_ns"],
                supported_raid_mode=data["supported_raid_mode"],
                cache=data.get("cache", ""),
                supported_bga_features=data["supported_bga_features"],
                support_stripe_size=data["support_stripe_size"],
                supported_features=data["supported_features"],
                root_complexes=root_complexes,
                end_points=end_points,
            )

        except Exception as e:
            logger.error("An unexpected error in fw_version: %s", e)
            self.fw_version = None
            raise


class BaseDeviceFactory(ABC):
    def __init__(self, api: BaseInterface):
        '''docstring'''
        self.api = api
        self.manufacturer = api.manufacturer

    @abstractmethod
    def initiate(self, **kwargs) -> BaseDevice:
        '''docstring'''
        pass


class ChunghuaFactory(BaseDeviceFactory):
    '''docstring'''
    def initiate(self, **kwargs) -> BaseDevice:
        '''docstring'''
        if self.manufacturer == 'VEN_1B4B':
            return Changhua(**kwargs)
        else:
            raise ValueError(f"Unsupported device type: {self.manufacturer}")
