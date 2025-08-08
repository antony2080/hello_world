from onvif import ONVIFCamera
from wsdiscovery.discovery import ThreadedWSDiscovery
from urllib.parse import urlparse
from zeep.transports import Transport
from requests import Session


def extract_host_from_xaddr(xaddr):
    try:
        return urlparse(xaddr).hostname
    except Exception:
        return None


def scan_onvif_hosts_sync():
    """
    Synchronously scans for ONVIF hosts on the network.
    Blocking! In async contexts, call via hass.async_add_executor_job or asyncio.to_thread.
    """
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


def try_login_and_get_info(ip, username, password, timeout=3):
    try:
        session = Session()
        session.timeout = timeout
        transport = Transport(session=session)
        cam = ONVIFCamera(
            ip, 80, username, password, no_cache=True, transport=transport
        )
        info = cam.devicemgmt.GetDeviceInformation()
        return info
    except Exception:
        return None
