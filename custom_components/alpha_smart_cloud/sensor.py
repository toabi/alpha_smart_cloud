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
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .coordinator import AlphaSmartCloudData, AlphaSmartCloudDataUpdateCoordinator
from .const import DOMAIN, PROP_BATTERY, PROP_HUMIDITY, PROP_IS_ONLINE, PROP_NAME, PROP_RSSI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud sensors."""
    api = entry.runtime_data.api
    coordinator = entry.runtime_data.coordinator

    devices_data = coordinator.data.devices
    group_names = coordinator.data.group_names

    entities = []
    for device in devices_data:
        device_id = device["deviceId"]
        group_id = device.get("groupId")
        room_name = group_names.get(group_id)

        device_data = coordinator.data.device_data.get(device_id)
        if not device_data:
            continue
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        if PROP_BATTERY in properties:
            entities.append(
                AlphaSmartCloudBatterySensor(
                    coordinator, api, device_data, room_name
                )
            )

        if PROP_RSSI in properties:
            entities.append(
                AlphaSmartCloudRSSISensor(coordinator, api, device_data, room_name)
            )

        # Add humidity sensor for climate devices (type "rbg")
        if device.get("type") == "rbg" and PROP_HUMIDITY in properties:
            entities.append(
                AlphaSmartCloudHumiditySensor(
                    coordinator, api, device_data, room_name
                )
            )

    async_add_entities(entities)


class AlphaSmartCloudSensor(
    CoordinatorEntity[AlphaSmartCloudDataUpdateCoordinator], SensorEntity
):
    """Base class for Alpha Smart Cloud sensors."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
        room_name: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = device_data["deviceId"]

        # Device info initialization
        device_info = device_data.get("deviceInfo", {})
        name = room_name or device_info.get("description", "Climate")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=name,
            manufacturer=device_info.get("oem"),
            model=device_info.get("type"),
        )

        self._update_from_data(device_data)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        # Check device availability based on online status
        if PROP_IS_ONLINE in properties:
            self._attr_available = bool(properties[PROP_IS_ONLINE]["value"])
        else:
            self._attr_available = False
            _LOGGER.debug("Device %s missing online status, marking sensor unavailable", self._device_id)

        if PROP_NAME in properties:
            self._attr_device_info["name"] = properties[PROP_NAME]["value"]

    @callback
    def _handle_coordinator_update(self) -> None:
        device_data = self.coordinator.data.device_data.get(self._device_id)
        if device_data:
            self._update_from_data(device_data)
        self.async_write_ha_state()


class AlphaSmartCloudBatterySensor(AlphaSmartCloudSensor):
    """Representation of an Alpha Smart Cloud battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
        room_name: str | None = None,
    ) -> None:
        """Initialize the battery sensor."""
        self._attr_name = "Battery"
        self._attr_unique_id = f"{device_data['deviceId']}_battery"
        super().__init__(coordinator, api, device_data, room_name)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        super()._update_from_data(device_data)
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        if PROP_BATTERY in properties:
            self._attr_native_value = properties[PROP_BATTERY]["value"]


class AlphaSmartCloudRSSISensor(AlphaSmartCloudSensor):
    """Representation of an Alpha Smart Cloud RSSI sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:wifi-strength-4"

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
        room_name: str | None = None,
    ) -> None:
        """Initialize the RSSI sensor."""
        self._attr_name = "Signal Strength"
        self._attr_unique_id = f"{device_data['deviceId']}_rssi"
        super().__init__(coordinator, api, device_data, room_name)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        super()._update_from_data(device_data)
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        if PROP_RSSI in properties:
            self._attr_native_value = properties[PROP_RSSI]["value"]


class AlphaSmartCloudHumiditySensor(AlphaSmartCloudSensor):
    """Representation of an Alpha Smart Cloud humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
        room_name: str | None = None,
    ) -> None:
        """Initialize the humidity sensor."""
        self._attr_name = "Humidity"
        self._attr_unique_id = f"{device_data['deviceId']}_humidity"
        super().__init__(coordinator, api, device_data, room_name)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        super()._update_from_data(device_data)
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}

        if PROP_HUMIDITY in properties:
            self._attr_native_value = properties[PROP_HUMIDITY]["value"]
