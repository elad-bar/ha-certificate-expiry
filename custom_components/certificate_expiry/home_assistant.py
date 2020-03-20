"""
This component provides support for Home Automation Manager (HAM).
For more details about this component, please refer to the documentation at
https://home-assistant.io/components/SSLCertificateExpirySensor/
"""
import sys
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .device_manager import DeviceManager
from .entity_manager import EntityManager
from .const import *

_LOGGER = logging.getLogger(__name__)


class SSLCertificateExpiryHomeAssistant:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self._hass = hass

        self._config_entry = entry

        self._integration_name = entry.data.get(CONF_NAME)
        self._certificate_path = entry.data.get(CONF_CERT_FILE)

        self._is_first_time_online = True
        self._is_initialized = False
        self._is_ready = False
        self._entity_manager = None
        self._device_manager = None
        self._remove_async_track_time = None

    @property
    def certificate_path(self):
        return self._certificate_path

    @property
    def integration_name(self):
        return self._integration_name

    @property
    def entity_manager(self) -> EntityManager:
        return self._entity_manager

    @property
    def device_manager(self) -> DeviceManager:
        return self._device_manager

    async def initialize(self):
        def finalize(event_time):
            self._hass.async_create_task(self.async_finalize(event_time))

        async_call_later(self._hass, 5, finalize)

    async def async_finalize(self, event_time):
        _LOGGER.debug(f"async_finalize called at {event_time}")

        self._device_manager = DeviceManager(self._hass, self)
        self._entity_manager = EntityManager(self._hass, self)

        self._hass.async_create_task(self.async_update_entry(self._config_entry, False))

        def update(now):
            self._hass.async_create_task(self.async_update(now))

        self._remove_async_track_time = async_track_time_interval(self._hass,
                                                                  update,
                                                                  SCAN_INTERVAL)

        self._is_initialized = True

    async def async_remove(self):
        _LOGGER.debug(f"async_remove called")

        unload = self._hass.config_entries.async_forward_entry_unload

        for domain in SIGNALS:
            self._hass.async_create_task(unload(self._config_entry, domain))

    async def async_update_entry(self, entry, clear_all):
        _LOGGER.info(f"async_update_entry: {self._config_entry.options}")
        self._is_ready = False

        self._config_entry = entry

        self._entity_manager.update_options(entry.options)

        if clear_all:
            await self._device_manager.async_remove_entry(self._config_entry.entry_id)

            await self.discover_all()
        else:
            await self.async_update(None)

    async def async_update(self, event_time):
        _LOGGER.debug(f"Starting async_update at {event_time}")

        try:
            self.entity_manager.update()

            self._is_ready = True

            await self.discover_all()
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f'Failed to update, Error: {ex}, Line: {line_number}')

    async def discover_all(self):
        if not self._is_ready or not self._is_initialized:
            return

        entity = self.entity_manager.get_entity_data()

        self.device_manager.update(entity)

        default_device_info = self.device_manager.get(self._integration_name)

        if CONF_NAME in default_device_info:
            for domain in SIGNALS:
                await self.discover(domain)

            self.entity_manager.clear_domain_states()

    async def discover(self, domain):
        signal = SIGNALS.get(domain)

        if signal is None:
            _LOGGER.error(f"Cannot discover domain {domain}")
            return

        unload = self._hass.config_entries.async_forward_entry_unload
        setup = self._hass.config_entries.async_forward_entry_setup

        entry = self._config_entry

        can_unload = self.entity_manager.get_domain_state(domain, DOMAIN_UNLOAD)
        can_load = self.entity_manager.get_domain_state(domain, DOMAIN_LOAD)
        can_notify = not can_load and not can_unload

        if can_unload:
            _LOGGER.info(f"Unloading domain {domain}")

            self._hass.async_create_task(unload(entry, domain))
            self.entity_manager.set_domain_state(domain, DOMAIN_LOAD, False)

        if can_load:
            _LOGGER.info(f"Loading domain {domain}")

            self._hass.async_create_task(setup(entry, domain))
            self.entity_manager.set_domain_state(domain, DOMAIN_UNLOAD, False)

        if can_notify:
            async_dispatcher_send(self._hass, signal)


def _get_ha_data(hass, name) -> SSLCertificateExpiryHomeAssistant:
    ha = hass.data[DOMAIN_DATA]
    ha_data = None

    if ha is not None:
        ha_data = ha.get(name)

    return ha_data
