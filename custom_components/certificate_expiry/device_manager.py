import sys
import logging
from homeassistant.helpers import device_registry as dr

from .const import *

_LOGGER = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self, hass, ha):
        self._hass = hass
        self._ha = ha

        self._devices = {}

        self._certificate_path = ha.certificate_path
        self._integration_name = ha.integration_name

    async def async_remove_entry(self, entry_id):
        device_reg = await dr.async_get_registry(self._hass)
        device_reg.async_clear_config_entry(entry_id)

    async def async_remove(self):
        for device_name in self._devices:
            device = self._devices[device_name]

            device_identifiers = device.get("identifiers")
            device_connections = device.get("connections", {})

            device_reg = await dr.async_get_registry(self._hass)

            device = device_reg.async_get_device(device_identifiers, device_connections)

            if device is not None:
                device_reg.async_remove_device(device.id)

    def get(self, name):
        return self._devices.get(name, {})

    def set(self, name, device_info):
        self._devices[name] = device_info

    def update(self, entity_data):
        try:
            current_device_info = self.get(DEFAULT_NAME)

            device_name = entity_data.get(ENTITY_NAME)

            device_info = {
                "identifiers": {
                    (DEFAULT_NAME, device_name)
                },
                "name": device_name,
                "manufacturer": entity_data.get(ENTITY_DEVICE_ISSUER),
                "model": entity_data.get(ENTITY_DEVICE_MODEL),
                "sw_version": entity_data.get(ENTITY_DEVICE_VERSION)
            }

            if current_device_info.get("name", "") != device_name:
                _LOGGER.info(f"{DEFAULT_NAME} device created: {device_info}")

                self.set(device_name, device_info)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Failed to generate system device, Error: {ex}, Line: {line_number}')
