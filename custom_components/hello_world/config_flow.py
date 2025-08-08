from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .api import UrmetCloudAPI
from .scanner import scan_onvif_hosts_sync, try_login_and_get_info


class HelloWorldConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.httpd_username = user_input.get("httpd_username")
            self.httpd_password = user_input.get("httpd_password")

            # Use UrmetCloudAPI to login and get camera list
            api = UrmetCloudAPI(self.httpd_username, self.httpd_password)
            login_ok = await api.login()
            if not login_ok:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_login_schema(),
                    errors={"base": "invalid_auth"},
                )

            camlist = await api.get_camera_list()
            onvif_hosts = await self.hass.async_add_executor_job(scan_onvif_hosts_sync)
            self.found_devices = []
            for cam in camlist:
                for ip in onvif_hosts:
                    info = await self.hass.async_add_executor_job(
                        try_login_and_get_info, ip, cam["cam_usr"], cam["cam_psw"]
                    )
                    if info and "1099" in info.Model:
                        self.found_devices.append(
                            {
                                "name": cam["cam_name"],
                                "uid": cam["cam_uid"],
                                "ip": ip,
                                "user": cam["cam_usr"],
                                "pass": cam["cam_psw"],
                            }
                        )
                        break

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
            return self.async_create_entry(
                title=f"{selected['name']} ({selected['ip']})",
                data={
                    "ip": selected["ip"],
                    "uid": selected["uid"],
                    "username": selected["user"],
                    "password": selected["pass"],
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
