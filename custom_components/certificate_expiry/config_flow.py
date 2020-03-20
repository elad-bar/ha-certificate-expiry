"""Config flow to configure SSLCertificateExpiry."""
import logging

from homeassistant import config_entries

from .const import *

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class CertificateExpiryFlowHandler(config_entries.ConfigFlow):
    """Handle a HPPrinter config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    _auth_error = False

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        _LOGGER.debug(f"Starting async_step_user of {DEFAULT_NAME}")

        fields = {
            vol.Required(CONF_NAME, DEFAULT_NAME): str,
            vol.Required(CONF_CERT_FILE): str
        }

        errors = None

        if user_input is not None:
            name = user_input.get(CONF_NAME)
            cert_file = user_input.get(CONF_CERT_FILE)

            for entry in self._async_current_entries():
                if entry.data[CONF_NAME] == name:
                    _LOGGER.warning(f"Certification ({name}) already configured")

                    return self.async_abort(reason="already_configured",
                                            description_placeholders={
                                                CONF_NAME: name
                                            })

            if errors is None:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_CERT_FILE: cert_file
                    },
                )

        return self.async_show_form(step_id="user", data_schema=vol.Schema(fields), errors=errors)

    async def async_step_import(self, info):
        """Import existing configuration from Certificate Expiry."""
        _LOGGER.debug(f"Starting async_step_import of {DEFAULT_NAME}")

        return self.async_create_entry(
            title=f"{DEFAULT_NAME} (import from configuration.yaml)",
            data={
                CONF_NAME: info.get(CONF_NAME),
                CONF_CERT_FILE: info.get(CONF_CERT_FILE)
            },
        )
