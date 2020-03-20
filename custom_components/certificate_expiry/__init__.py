"""
This component provides support for SSLCertificateExpiry.
For more details about this component, please refer to the documentation at
https://home-assistant.io/components/CertificateExpiry/
"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import VERSION
from .const import *
from .home_assistant import SSLCertificateExpiryHomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    _LOGGER.debug(f"Legacy setup of {hass} with {config}")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a CertificateExpiry component."""
    _LOGGER.debug(f"Loading {DOMAIN} domain")

    entry_data = entry.data
    name = entry_data.get(CONF_NAME)

    if DOMAIN_DATA not in hass.data:
        hass.data[DOMAIN_DATA] = {}

    if name in hass.data[DOMAIN_DATA]:
        _LOGGER.info(f"CertificateExpiry {name} already defined")
        return False

    ha = SSLCertificateExpiryHomeAssistant(hass, entry)
    await ha.initialize()

    hass.data[DOMAIN_DATA][name] = ha

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    data = hass.data[DOMAIN_DATA]
    name = entry.data.get(CONF_NAME)

    if name in data:
        ha: SSLCertificateExpiryHomeAssistant = data[name]
        await ha.async_remove()

        del hass.data[DOMAIN_DATA][name]

        return True

    return False
