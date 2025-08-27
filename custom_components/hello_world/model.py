from dataclasses import dataclass


@dataclass
class DeviceInfo:
    manufacturer: str | None = None
    model: str | None = None
    fw_version: str | None = None
    serial_number: str | None = None
    mac: str | None = None


@dataclass
class Camera:
    cam_uid: str
    cam_name: str
    cam_desc: str
    cam_psw: str
    cam_position: str
    cam_permission: str
    app_lite: str
    dev_type: str
    iotc_type: str
    device_acl: str
    nvr_port: str
    cam_usr: str
