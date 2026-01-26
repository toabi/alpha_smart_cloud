"""Support for Alpha Smart Cloud sensors."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .const import DOMAIN, PROP_BATTERY, PROP_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud sensors."""
    api = entry.runtime_data

    # Fetch devices directly
    devices_data = await hass.async_add_executor_job(api.get_devices)

    entities = []
    for device in devices_data:
        device_id = device["deviceId"]
        device_data = await hass.async_add_executor_job(
            api.get_device_with_template, device_id
        )
        # Only add battery sensor if the device has a battery property
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}
        if PROP_BATTERY in properties:
            entities.append(AlphaSmartCloudBatterySensor(api, device_data))

    async_add_entities(entities)


class AlphaSmartCloudBatterySensor(SensorEntity):
    """Representation of an Alpha Smart Cloud battery sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
    ) -> None:
        """Initialize the battery sensor."""
        self._api = api
        self._device_id = device_data["deviceId"]
        self._attr_name = "Battery"
        self._attr_unique_id = f"{self._device_id}_battery"

        # Device info initialization
        device_info = device_data.get("deviceInfo", {})
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device_info.get("description", "Climate"),
            manufacturer=device_info.get("oem"),
            model=device_info.get("type"),
        )

        self._update_from_data(device_data)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        if PROP_NAME in properties:
            self._attr_device_info["name"] = properties[PROP_NAME]["value"]

        if PROP_BATTERY in properties:
            self._attr_native_value = properties[PROP_BATTERY]["value"]

    async def async_update(self) -> None:
        """Fetch new state data for this device."""
        device_data = await self.hass.async_add_executor_job(
            self._api.get_device_with_template, self._device_id
        )
        self._update_from_data(device_data)
