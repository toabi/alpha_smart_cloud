"""Support for Alpha Smart Cloud vacation mode switch."""
from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .coordinator import AlphaSmartCloudData, AlphaSmartCloudDataUpdateCoordinator
from .const import DOMAIN, PROP_VACATION_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud switch."""
    api = entry.runtime_data.api
    coordinator = entry.runtime_data.coordinator

    homes = coordinator.data.homes
    devices = coordinator.data.devices

    # Map home_id to its first rbg device to track vacation mode
    home_to_device = {}
    for device in devices:
        if device.get("type") == "rbg" and "homeId" in device:
            home_id = device["homeId"]
            if home_id not in home_to_device:
                home_to_device[home_id] = device["deviceId"]

    entities = []
    for home in homes:
        home_id = home["id"]
        if home_id in home_to_device:
            entities.append(
                AlphaSmartCloudVacationSwitch(
                    coordinator, api, home, home_to_device[home_id]
                )
            )

    async_add_entities(entities)


class AlphaSmartCloudVacationSwitch(
    CoordinatorEntity[AlphaSmartCloudDataUpdateCoordinator], SwitchEntity
):
    """Representation of an Alpha Smart Cloud vacation mode switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:airplane"

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        home: dict[str, Any],
        reference_device_id: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = api
        self._home_id = home["id"]
        self._reference_device_id = reference_device_id
        self._attr_name = "Vacation Mode"
        self._attr_unique_id = f"{self._home_id}_vacation_mode"
        self._attr_is_on = None
        self._pending_updates: dict[str, tuple[Any, float]] = {}

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._home_id)},
            name=home.get("name", "Home"),
            manufacturer="Alpha Smart",
            model="Home",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for this home."""
        # We poll one device in the home to get the vacation mode status
        device_data = self.coordinator.data.device_data.get(self._reference_device_id)
        if not device_data:
            self._attr_available = False
            self.async_write_ha_state()
            return

        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}
        if PROP_VACATION_MODE in properties:
            is_on = properties[PROP_VACATION_MODE]["value"] == "on"
            now = time.monotonic()

            if PROP_VACATION_MODE in self._pending_updates:
                pending_val, timestamp = self._pending_updates[PROP_VACATION_MODE]
                if now - timestamp > 15 or is_on == pending_val:
                    del self._pending_updates[PROP_VACATION_MODE]
                else:
                    is_on = pending_val

            self._attr_is_on = is_on
            self._attr_available = True
        else:
            self._attr_available = False

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on vacation mode for home %s", self._home_id)
        self._pending_updates[PROP_VACATION_MODE] = (True, time.monotonic())
        self._attr_is_on = True
        self.async_write_ha_state()

        try:
            await self.hass.async_add_executor_job(
                self._api.set_home_vacation_mode, self._home_id, "on"
            )
            _LOGGER.debug("Successfully turned on vacation mode for home %s", self._home_id)
        except Exception as err:
            _LOGGER.error("Failed to turn on vacation mode for home %s: %s", self._home_id, err)
            if PROP_VACATION_MODE in self._pending_updates:
                del self._pending_updates[PROP_VACATION_MODE]
            self._attr_is_on = False
            self.async_write_ha_state()
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off vacation mode for home %s", self._home_id)
        self._pending_updates[PROP_VACATION_MODE] = (False, time.monotonic())
        self._attr_is_on = False
        self.async_write_ha_state()

        try:
            await self.hass.async_add_executor_job(
                self._api.set_home_vacation_mode, self._home_id, "off"
            )
            _LOGGER.debug("Successfully turned off vacation mode for home %s", self._home_id)
        except Exception as err:
            _LOGGER.error("Failed to turn off vacation mode for home %s: %s", self._home_id, err)
            if PROP_VACATION_MODE in self._pending_updates:
                del self._pending_updates[PROP_VACATION_MODE]
            self._attr_is_on = True
            self.async_write_ha_state()
            raise
