from onvif import ONVIFCamera
from wsdiscovery.discovery import ThreadedWSDiscovery
from urllib.parse import urlparse
import asyncio
import logging
import socket


def extract_host_from_xaddr(xaddr):
    try:
        return urlparse(xaddr).hostname
    except Exception:
        return None


def scan_onvif_hosts_sync():
    wsd = ThreadedWSDiscovery()
    wsd.start()
    services = wsd.searchServices()
    results = set()
    for service in services:
        for xaddr in service.getXAddrs():
            host = extract_host_from_xaddr(xaddr)
            if host:
                results.add(host)
    wsd.stop()
    return list(results)


def is_port_open(ip, port, timeout=0.5):
    """Quickly check if a TCP port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((ip, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


async def try_login_and_get_info(ip, username, password, cam):
    if not (is_port_open(ip, 80) or is_port_open(ip, 554)):
        logging.warning(f"Ports 80 and 554 are not open for IP: {ip}")
        return None
    cam_device = None
    try:
        cam_device = ONVIFCamera(ip, 80, username, password)
        devicemgmt = await cam_device.create_devicemgmt_service()
        info = await devicemgmt.GetDeviceInformation()
        logging.info(f"Successfully retrieved device info for IP: {ip}")
        await cam_device.close()
        return {"info": info, "cam": cam, "ip": ip}
    except Exception as e:
        logging.error(f"Failed to login to ONVIF device at {ip}: {e}")
        return None
    finally:
        if cam_device:
            try:
                cam_device.close()
            except Exception:
                pass
