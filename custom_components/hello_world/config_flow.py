from homeassistant import config_entries
import voluptuous as vol
import asyncio
from .const import DOMAIN
from .api import UrmetCloudAPI
from .scanner import (
    scan_onvif_hosts_sync,
    try_login_and_get_info,
    register_device_in_registry,
)
from .model import DeviceInfo, Camera  # Ensure DeviceInfo and Camera are imported
import logging

_LOGGER = logging.getLogger(__name__)


class HelloWorldConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            username = user_input.get("httpd_username")
            password = user_input.get("httpd_password")

            api = UrmetCloudAPI(username, password)
            login_ok = await api.login()
            if not login_ok:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_login_schema(),
                    errors={"base": "invalid_auth"},
                )
            camlist = await api.get_camera_list()
            _LOGGER.info("Retrieved %d cameras from cloud", len(camlist))
            onvif_hosts = await self.hass.async_add_executor_job(scan_onvif_hosts_sync)
            _LOGGER.info("Found %d ONVIF hosts on network", len(onvif_hosts))
            self.found_devices = []
            # Prepare all tasks
            tasks = []
            # Updated Camera instantiation to match the new class definition
            for cam in camlist:
                camera_obj = Camera(
                    cam_name=cam["cam_name"],
                    cam_uid=cam["cam_uid"],
                    cam_usr=cam["cam_usr"],
                    cam_psw=cam["cam_psw"],
                )
                for ip in onvif_hosts:
                    tasks.append(try_login_and_get_info(ip, camera_obj))
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, dict) and result.get("device_info"):
                    info = result["device_info"]
                    cam = result["cam"]
                    ip = result["ip"]
                    if info.manufacturer == "URMET" and "1099" in info.model:
                        _LOGGER.info("Matched camera %s with IP %s", cam.cam_uid, ip)
                        self.found_devices.append(
                            {
                                "name": cam.cam_name,
                                "uid": cam.cam_uid,
                                "user": cam.cam_usr,
                                "pass": cam.cam_psw,
                                "ip": ip,
                                "device_info": {
                                    "manufacturer": info.manufacturer,
                                    "model": info.model,
                                    "fw_version": info.fw_version,
                                    "serial_number": info.serial_number,
                                    "mac": info.mac,
                                },
                            }
                        )

            return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_login_schema(),
        )

    async def async_step_select_device(self, user_input=None):
        options = {f"{dev['name']} ({dev['ip']})": dev for dev in self.found_devices}

        if user_input:
            selected_label = user_input["device"]
            selected = options[selected_label]

            # Register the selected device in the device registry
            device_info = DeviceInfo(
                manufacturer=selected["device_info"]["manufacturer"],
                model=selected["device_info"]["model"],
                fw_version=selected["device_info"]["fw_version"],
                serial_number=selected["device_info"]["serial_number"],
                mac=selected["device_info"]["mac"],
            )
            await register_device_in_registry(self.hass, selected, device_info)

            return self.async_create_entry(
                title=f"{selected['name']} ({selected['ip']})",
                data={
                    "name": selected["name"],
                    "ip": selected["ip"],
                    "uid": selected["uid"],
                    "username": selected["user"],
                    "password": selected["pass"],
                    "device_info": selected["device_info"],
                },
            )

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {vol.Required("device"): vol.In(list(options.keys()))}
            ),
        )

    def _get_login_schema(self):
        return vol.Schema(
            {
                vol.Required("httpd_username"): str,
                vol.Required("httpd_password"): str,
            }
        )
