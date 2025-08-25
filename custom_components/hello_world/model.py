from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """Represent device information."""

    manufacturer: str | None = None
    model: str | None = None
    fw_version: str | None = None
    serial_number: str | None = None
    mac: str | None = None
