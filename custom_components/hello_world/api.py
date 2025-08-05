import aiohttp
import xml.etree.ElementTree as ET


class UrmetAPI:
    def __init__(self, host):
        self._host = host
        self._auth = aiohttp.BasicAuth("admin", "admin")

    async def get_motion_detected(self):
        url = f"http://{self._host}/Alarm/MotionStatus"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self._auth) as resp:
                xml = await resp.text()
                root = ET.fromstring(xml)
                return root.findtext(".//Motion") == "on"
