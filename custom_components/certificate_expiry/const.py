from datetime import timedelta

import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_NAME
from homeassistant.components.sensor import DOMAIN as DOMAIN_SENSOR

DOMAIN = "certificate_expiry"

VERSION = '1.0.1'

DEFAULT_NAME = 'Certificate Expiry'
DEFAULT_PORT = 443
DOMAIN_DATA = f"{DOMAIN}_data"

CONF_CERT_FILE = 'cert_file'
ATTR_SUBJECT = 'Subject'

SIGNAL_UPDATE_SENSOR = f"{DEFAULT_NAME}_{DOMAIN_SENSOR}_SIGNLE_UPDATE"
SIGNAL_SENSOR = "DOMAIN"
SIGNALS = [SIGNAL_UPDATE_SENSOR]

DOMAIN_LOAD = "load"
DOMAIN_UNLOAD = "unload"

SCAN_INTERVAL = timedelta(hours=12)

ENTITY_ICON = 'icon'
ENTITY_STATE = 'state'
ENTITY_ATTRIBUTES = 'attributes'
ENTITY_NAME = 'name'
ENTITY_DEVICE_ISSUER = "device-issuer"
ENTITY_DEVICE_VERSION = "version"
ENTITY_DEVICE_MODEL = "model"
