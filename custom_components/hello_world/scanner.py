from onvif import ONVIFCamera
from wsdiscovery.discovery import ThreadedWSDiscovery
from wsdiscovery.qname import QName
from wsdiscovery.scope import Scope
from urllib.parse import urlparse
import logging
from .model import DeviceInfo, Camera
from .const import DOMAIN
from homeassistant.helpers import device_registry as dr


def extract_host_from_xaddr(xaddr):
    try:
        return urlparse(xaddr).hostname
    except Exception:
        return None


def scan_onvif_hosts_sync():
    wsd = ThreadedWSDiscovery(ttl=4, relates_to=True)
    wsd.start()
    services = wsd.searchServices(
        types=[
            QName(
                "http://www.onvif.org/ver10/network/wsdl",
                "NetworkVideoTransmitter",
                "dp0",
            )
        ],
        scopes=[Scope("onvif://www.onvif.org/Profile/Streaming")],
    )
    results = set()
    for service in services:
        for xaddr in service.getXAddrs():
            host = extract_host_from_xaddr(xaddr)
            if host:
                results.add(host)
    wsd.stop()
    return list(results)


async def register_device_in_registry(
    hass, entry_id, cam: Camera, device_info: DeviceInfo
):
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, device_info.mac)},
        identifiers={(DOMAIN, cam.cam_uid)},
        manufacturer=device_info.manufacturer,
        model=device_info.model,
        name=cam.cam_name,
        sw_version=device_info.fw_version,
    )


async def try_login_and_get_info(ip, cam: Camera):
    cam_device = None
    try:
        cam_device = ONVIFCamera(ip, 80, cam.cam_usr, cam.cam_psw)
        devicemgmt = await cam_device.create_devicemgmt_service()
        info = await devicemgmt.GetDeviceInformation()
        logging.info(f"Successfully retrieved device info for IP: {ip}")

        mac_address = None
        try:
            network_interfaces = await devicemgmt.GetNetworkInterfaces()
            if network_interfaces:
                for interface in network_interfaces:
                    if interface and interface.MACAddress:
                        mac_address = interface.MACAddress
                        break
        except Exception as e:
            logging.warning(f"Failed to retrieve MAC address for IP {ip}: {e}")

        # Create DeviceInfo with MAC address
        device_info = DeviceInfo(
            manufacturer=info.Manufacturer,
            model=info.Model,
            fw_version=info.FirmwareVersion,
            serial_number=info.SerialNumber,
            mac=mac_address,
        )

        await cam_device.close()
        return {"device_info": device_info, "cam": cam, "ip": ip}
    except Exception as e:
        logging.warning(f"Failed to login to ONVIF device at {ip}: {e}")
        return None
    finally:
        if cam_device:
            try:
                await cam_device.close()
            except Exception as e:
                logging.warning(f"Failed to close ONVIF device at {ip}: {e}")
