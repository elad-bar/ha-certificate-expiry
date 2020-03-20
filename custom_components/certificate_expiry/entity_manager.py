import logging

from datetime import datetime

from homeassistant.const import ATTR_FRIENDLY_NAME

from OpenSSL import crypto as c

from .const import *

_LOGGER = logging.getLogger(__name__)


def _get_camera_binary_sensor_key(topic, event_type):
    key = f"{topic}_{event_type}".lower()

    return key


class EntityManager:
    def __init__(self, hass, ha):
        self._hass = hass
        self._ha = ha

        self._entities = {}
        self._entry_loaded_state = {}
        self._domain_states: dict = {}
        self._certificate = None
        self._certificate_expiry = None
        self._certificate_path = ha.certificate_path
        self._integration_name = ha.integration_name

        for domain in SIGNALS:
            self.clear_entities(domain)
            self.set_domain_state(domain, DOMAIN_LOAD, False)
            self.set_domain_state(domain, DOMAIN_UNLOAD, False)
            self.set_entry_loaded_state(domain, False)

        self.load_certificate()

    def set_entry_loaded_state(self, domain, has_entities):
        self._entry_loaded_state[domain] = has_entities

    def get_entry_loaded_state(self, domain):
        return self._entry_loaded_state.get(domain, False)

    def clear_entities(self, domain):
        self._entities[domain] = {}

    def get_entities(self, domain):
        return self._entities.get(domain, {})

    def get_entity(self, domain, name):
        entities = self.get_entities(domain)
        entity = {}
        if entities is not None:
            entity = entities.get(name, {})

        return entity

    def set_entity(self, domain, name, data):
        entities = self._entities.get(domain)

        if entities is None:
            self._entities[domain] = {}

            entities = self._entities.get(domain)

        entities[name] = data

    def update(self):
        previous_keys = {}
        for domain in SIGNALS:
            previous_keys[domain] = ','.join(self.get_entities(domain).keys())

            self.clear_entities(domain)

        self.create_sensor()

        for domain in SIGNALS:
            domain_keys = self.get_entities(domain).keys()
            previous_domain_keys = previous_keys[domain]
            entry_loaded_state = self.get_entry_loaded_state(domain)

            if len(domain_keys) > 0:
                current_keys = ','.join(domain_keys)

                if current_keys != previous_domain_keys:
                    self.set_domain_state(domain, DOMAIN_LOAD, True)

                    if len(previous_domain_keys) > 0:
                        self.set_domain_state(domain, DOMAIN_UNLOAD, entry_loaded_state)
            else:
                if len(previous_domain_keys) > 0:
                    self.set_domain_state(domain, DOMAIN_UNLOAD, entry_loaded_state)

    def get_domain_state(self, domain, key):
        if domain not in self._domain_states:
            self._domain_states[domain] = {}

        return self._domain_states[domain].get(key, False)

    def set_domain_state(self, domain, key, state):
        if domain not in self._domain_states:
            self._domain_states[domain] = {}

        self._domain_states[domain][key] = state

    def clear_domain_states(self):
        for domain in SIGNALS:
            self.set_domain_state(domain, DOMAIN_LOAD, False)
            self.set_domain_state(domain, DOMAIN_UNLOAD, False)

    def get_domain_states(self):
        return self._domain_states

    def create_sensor(self):
        try:
            if self._certificate is None:
                _LOGGER.error(f"Certificate {self._integration_name} is not loaded")

                return

            entity = self.get_entity_data()
            entity_name = entity.get(ENTITY_NAME)

            self.set_entity(DOMAIN_SENSOR, entity_name, entity)
        except Exception as ex:
            _LOGGER.error(f'Failed to create sensor, Error: {str(ex)}')

    def get_entity_data(self):
        try:
            if self._certificate is None:
                _LOGGER.error(f"Certificate {self._integration_name} is not loaded")

                return

            entity_name = f'{self._integration_name}'

            not_after = self._certificate.get_notAfter().decode("utf-8")

            certificate_expiry = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")
            time_left = certificate_expiry - datetime.today()

            state = time_left.days

            attributes = {
                CONF_CERT_FILE: self._certificate_path,
                ATTR_FRIENDLY_NAME: entity_name,
                ENTITY_DEVICE_ISSUER: self._certificate.get_issuer(),
                ATTR_SUBJECT: self._certificate.get_subject(),
                ENTITY_DEVICE_VERSION: self._certificate.get_version(),
            }

            entity = {
                ENTITY_NAME: entity_name,
                ENTITY_STATE: state,
                ENTITY_ATTRIBUTES: attributes,
                ENTITY_ICON: "mdi:timer-sand",
                ENTITY_DEVICE_ISSUER: attributes.get(ENTITY_DEVICE_ISSUER),
                ENTITY_DEVICE_VERSION: attributes.get(ENTITY_DEVICE_VERSION),
                ENTITY_DEVICE_MODEL: attributes.get(ATTR_SUBJECT)
            }

            return entity
        except Exception as ex:
            _LOGGER.error(f'Failed to create sensor, Error: {str(ex)}')

    def load_certificate(self):
        """Fetch the certificate information."""
        try:

            with open(self._certificate_path, "rb") as certificate_file:
                certificate_content = certificate_file.read()

            if certificate_content is not None:
                self._certificate = c.load_certificate(c.FILETYPE_PEM, certificate_content)

        except Exception as ex:
            _LOGGER.error(f'Failed to parse certificate: {self._certificate_path}, Error: {str(ex)}')
