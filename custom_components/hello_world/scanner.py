from onvif import ONVIFCamera
from wsdiscovery.discovery import ThreadedWSDiscovery
from wsdiscovery.qname import QName
from wsdiscovery.scope import Scope
from urllib.parse import urlparse
import logging
from .model import DeviceInfo


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


async def try_login_and_get_info(ip, username, password, cam):
    cam_device = None
    try:
        cam_device = ONVIFCamera(ip, 80, username, password)
        devicemgmt = await cam_device.create_devicemgmt_service()
        info = await devicemgmt.GetDeviceInformation()
        interfaces = await devicemgmt.GetNetworkInterfaces()
        mac = None
        for iface in interfaces:
            if iface.Enabled:
                mac = getattr(iface.Info, "HwAddress", None)
        logging.info(f"Successfully retrieved device info for IP: {ip}")

        device_info = DeviceInfo(
            manufacturer=info.Manufacturer,
            model=info.Model,
            fw_version=info.FirmwareVersion,
            serial_number=info.SerialNumber,
            mac=mac,
        )

        await cam_device.close()
        return {"info": device_info, "cam": cam, "ip": ip}
    except Exception as e:
        logging.warning(f"Failed to login to ONVIF device at {ip}: {e}")
        return None
    finally:
        if cam_device:
            try:
                await cam_device.close()
            except Exception as e:
                logging.warning(f"Failed to close ONVIF device at {ip}: {e}")
