"""
Counter for the days until an HTTPS (TLS) certificate will expire.
For more details about this sensor please refer to the documentation at
https://home-assistant.io/components/sensor.cert_expiry/
"""
import logging
from datetime import timedelta
from datetime import datetime
from OpenSSL import crypto as c

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME)
from homeassistant.helpers.entity import Entity

from .const import *

REQUIREMENTS = ['pyOpenSSL']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=12)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CERT_FILE): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up certificate expiry sensor."""
    sensor_name = config.get(CONF_NAME)
    certificate_path = config.get(CONF_CERT_FILE)

    ssl_entity = SSLCertificateExpiry(sensor_name, certificate_path)

    add_entities([ssl_entity], True)


class SSLCertificateExpiry(Entity):
    """Implementation of the certificate expiry sensor."""

    def __init__(self, sensor_name, certificate_path):
        """Initialize the sensor."""
        self._certificate_path = certificate_path
        self._name = sensor_name
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return 'days'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:certificate'

    def update(self):
        """Fetch the certificate information."""
        try:

            with open(self._certificate_path, "rb") as certificate_file:
                certificate_content = certificate_file.read()

            if certificate_content is not None:
                cert = c.load_certificate(c.FILETYPE_PEM, certificate_content)
                not_after = cert.get_notAfter().decode("utf-8")

                timestamp = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")

                expiry = timestamp - datetime.today()
                self._state = expiry.days

        except Exception as ex:
            _LOGGER.error(f'Failed to parse certificate: {self._certificate_path}, Error: {str(ex)}')
            return
