import aiohttp
import xml.etree.ElementTree as ET
from .const import URMET_CLOUD_BASE_URL
import json


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


# Urmet Cloud API for async login and camera list retrieval
class UrmetCloudAPI:
    LOGIN_URL = f"{URMET_CLOUD_BASE_URL}/tool/index.php"
    CAMLIST_URL = f"{URMET_CLOUD_BASE_URL}/tool/webapi/private/index.php/mycamlist"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session_cookie = None

    async def login(self):
        data = {
            "httpd_username": self.username,
            "httpd_password": self.password,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.LOGIN_URL, data=data) as resp:
                if resp.status == 200:
                    self.session_cookie = resp.cookies.output(header="", sep="; ")
                    return True
                return False

    async def get_camera_list(self):
        if not self.session_cookie:
            raise Exception("Not logged in")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": self.session_cookie,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.CAMLIST_URL, headers=headers) as resp:
                text = await resp.text()

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    raise Exception(f"Invalid JSON content:\n{text}")
