import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_SERIAL, DEFAULT_TIME, CONF_SERIAL, CONF_REFRESH

@callback
def edl21_entries(hass: HomeAssistant):
    """Return the site_ids for the domain."""
    return {
        (entry.data[CONF_SERIAL])
        for entry in hass.config_entries.async_entries(DOMAIN)
    }


class Edl21ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors = {}

    def _site_in_configuration_exists(self, site_id) -> bool:
        """Return True if site_id exists in configuration."""
        if site_id in edl21_entries(self.hass):
            return True
        return False

    async def async_step_user(self, user_input=None):
        """Step when user initializes a integration."""
        self._errors = {}
        if user_input is not None:
            name = slugify(user_input.get(CONF_NAME, DEFAULT_NAME))
            if self._site_in_configuration_exists(user_input[CONF_NAME]):
                self._errors[CONF_NAME] = "already_configured"
            else:
                serial = user_input[CONF_SERIAL]
                time = user_input[CONF_REFRESH]
                return self.async_create_entry(
                    title=name, data={CONF_SERIAL: serial, CONF_REFRESH: time}
                )
        else:
            user_input = {}
            user_input[CONF_NAME] = DEFAULT_NAME
            user_input[CONF_SERIAL] = DEFAULT_SERIAL
            user_input[CONF_REFRESH] = DEFAULT_TIME


        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_NAME)
                    ): str,
                    vol.Required(CONF_SERIAL, default=user_input[CONF_SERIAL]): str,
                    vol.Required(CONF_REFRESH, default=user_input[CONF_REFRESH]): int,
                }
            ),
            errors=self._errors,
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        if self._site_in_configuration_exists(user_input[CONF_SERIAL]):
            return self.async_abort(reason="already_configured")
        return await self.async_step_user(user_input)
