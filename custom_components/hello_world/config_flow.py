from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class HelloWorldConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user provides host and login credentials."""
        if user_input is not None:
            # Dummy login validation
            host = user_input.get("host")
            username = user_input.get("username")
            password = user_input.get("password")

            if (
                host and username == "admin" and password == "admin"
            ):  # Dummy credentials
                # Simulate retrieving a camera stream and control options
                self.devices = ["Camera Stream"]
                return await self.async_step_select_device()
            else:
                errors = {"base": "invalid_credentials"}
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_login_schema(),
                    errors=errors,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_login_schema(),
        )

    async def async_step_select_device(self, user_input=None):
        """Handle the step to select a device."""
        if user_input is not None:
            selected_device = user_input.get("device")
            return self.async_create_entry(
                title=f"Hello World - {selected_device}",
                data={"device": selected_device},
            )

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(self.devices),
                }
            ),
        )

    def _get_login_schema(self):
        """Return the schema for the login step."""
        return vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )
