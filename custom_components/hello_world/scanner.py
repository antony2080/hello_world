from onvif import ONVIFCamera
from wsdiscovery.discovery import ThreadedWSDiscovery
from urllib.parse import urlparse
import socket
import logging


def extract_host_from_xaddr(xaddr):
    try:
        return urlparse(xaddr).hostname
    except Exception:
        return None


def is_port_open(ip, port, timeout=0.5):
    """Quickly check if a TCP port is open."""
    try:
        with socket.create_connection((ip, port), timeout):
            return True
    except (socket.timeout, OSError):
        return False


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


def try_login_and_get_info(ip, username, password, timeout=2):
    if not (is_port_open(ip, 80) or is_port_open(ip, 554)):
        logging.warning(f"Ports 80 and 554 are not open for IP: {ip}")
        return None
    try:
        cam = ONVIFCamera(ip, 80, username, password)
        info = cam.devicemgmt.GetDeviceInformation()
        logging.info(f"Successfully retrieved device info for IP: {ip}")
        return info
    except Exception as e:
        logging.error(f"Failed to login to ONVIF device at {ip}: {e}")
        return None
