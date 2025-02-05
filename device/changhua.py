# Contents of device/1b4b_2241.py
'''Copyright (c) 2025 Jaron Cheng'''
# import json
import logging
import re
from abc import ABC
from abc import abstractmethod
from commandline.mnv_cli import BaseCLI
from interface.application import BaseInterface
from interface.application import NVMeController
from interface.application import RootComplex
from interface.application import EndPoint
from interface.application import VirtualDrive
from unit.log_handler import get_logger

logger = get_logger(__name__, logging.INFO)


class BaseDevice(ABC):
    '''This is a docstring'''
    def __init__(self, command: BaseCLI):
        '''This is a docstring'''
        self.cmd = command
        self._controller_info = None
        self._virtual_drive_info = []


class Beidou(BaseDevice):
    @property
    def controller_info(self) -> NVMeController:
        try:
            hba_info = self.cmd.interpret('info -o hba')
            logger.debug('hba_info = %s', hba_info)
            data = {}
            root_complexes = []
            end_points = []
            current_section = None

            if isinstance(hba_info, list):
                lines = hba_info
            elif isinstance(hba_info, str):
                lines = hba_info.splitlines()
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

            self._controller_info = NVMeController(
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
            return self._controller_info

        except Exception as e:
            logger.error("An unexpected error in controller_info: %s", e)
            self._contrller_info = None
            raise

    @property
    def virtual_drive_info(self) -> VirtualDrive:
        try:
            vd_info = self.cmd.interpret('info -o vd')
            logger.debug('vd_info = %s', vd_info)
            virtual_drives = []
            data = {}
            pd_ids = []

            if isinstance(vd_info, list):
                lines = vd_info
            elif isinstance(vd_info, str):
                lines = vd_info.splitlines()
            else:
                raise TypeError("Invalid output type, expected str or list")

            for line in lines:
                match = re.match(r"(.*?):\s+(.*)", line)
                if match:
                    key, value = match.groups()
                    key = re.sub(r'[^a-zA-Z0-9_]', '_', key.lower())
                    logger.debug("%s: %s", key, value)

                    if key.startswith("vd_id"):
                        logger.debug("value = %s", value)
                        root_id = int(value)
                        virtual_drives.append(VirtualDrive(
                                vd_id=root_id,
                                name="",
                                status="",
                                importable="",
                                raid_mode="",
                                size="",
                                pd_count="",
                                pds="",
                                stripe_block_size="",
                                sector_size="",
                                total_of_vd=""
                            )
                        )
                    elif key.startswith("pds"):
                        if not pd_ids:
                            pds = re.findall(r'\d+', value)
                            logger.debug("pds = %s", pds)
                            pd_ids = list(map(int, pds))
                            logger.debug("pd_ids = %s", pd_ids)
                    else:
                        data[key] = value

            logger.debug("data = %s", data)
            # Convert specific values to correct types
            int_fields = ["vd_id", "pd_count", "total___of_vd"]
            for int_field in int_fields:
                data[int_field] = int(data.get(int_field, 0))

            list_fields = ["name", "status", "importable", "raid_mode",
                           "size", "stripe_block_size", "sector_size"]
            for list_field in list_fields:
                data[list_field] = data.get(list_field, "")

            for virtual_drive in virtual_drives:
                self._virtual_drive_info.append(VirtualDrive(
                        vd_id=virtual_drive.vd_id,
                        name=data.get("name", ""),
                        status=data.get("status", ""),
                        importable=data.get("importable", ""),
                        raid_mode=data.get("raid_mode", ""),
                        size=data.get("size", ""),
                        pd_count=data.get("pd_count", ""),
                        pds=pd_ids,
                        stripe_block_size=data.get("stripe_block_size", ""),
                        sector_size=data.get("sector_size", ""),
                        total_of_vd=data.get("total___of_vd")
                    )
                )
                return self._virtual_drive_info

        except Exception as e:
            logger.error("An unexpected error in virtual_drive_info: %s", e)
            self._virtual_drive_info = None
            raise


class BaseDeviceFactory(ABC):
    def __init__(self, api: BaseInterface):
        '''docstring'''
        self.api = api
        self.manufacturer = api.manufacturer
        self.device = api.nvme_controller.did

    @abstractmethod
    def initiate(self, **kwargs) -> BaseDevice:
        '''docstring'''
        pass


class ChanghuaFactory(BaseDeviceFactory):
    '''docstring'''
    def initiate(self, **kwargs) -> BaseDevice:
        '''docstring'''
        if self.manufacturer == 'VEN_1B4B':
            if self.device == '0x2241':
                return Beidou(**kwargs)
            else:
                raise ValueError(f"Unsupported device type: {self.device}")
        else:
            raise ValueError(f"Unsupported manufacturer: {self.manufacturer}")
