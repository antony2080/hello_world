import aiohttp
import xml.etree.ElementTree as ET
from .const import URMET_CLOUD_BASE_URL
import json


class CameraLocalAPI:
    def __init__(self, host, username, password):
        self._host = host
        self._auth = aiohttp.BasicAuth(username, password)

    async def get_alarm_enabled(self):
        url = f"http://{self._host}/System/AudioAlarmConfig"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self._auth) as resp:
                if resp.status == 200:
                    xml = await resp.text()
                    try:
                        root = ET.fromstring(xml)
                        enable = root.findtext("Enable")
                        return enable and enable.lower() == "true"
                    except Exception:
                        pass
        return None

    async def get_ircut_mode(self):
        url = f"http://{self._host}/Images/1/IrCutFilter"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=self._auth) as resp:
                if resp.status == 200:
                    xml = await resp.text()
                    try:
                        root = ET.fromstring(xml)
                        mode = root.findtext("Mode")
                        return mode
                    except Exception:
                        pass
        return None


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
