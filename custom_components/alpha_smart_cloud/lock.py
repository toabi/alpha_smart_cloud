"""Support for Alpha Smart Cloud lock mode."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .const import DOMAIN, PROP_LOCK_MODE, PROP_NAME

_LOGGER = logging.getLogger(__name__)

_LOCK_PAYLOAD_KEYS = (
    "standby",
    "menu",
    "targetTemp",
    "reserved1",
    "reserved2",
    "reserved3",
    "reserved4",
    "reserved5",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud lock entities."""
    api = entry.runtime_data

    devices_data = await hass.async_add_executor_job(api.get_devices)

    entities: list[AlphaSmartCloudDeviceLock] = []
    for device in devices_data:
        device_id = device["deviceId"]
        device_data = await hass.async_add_executor_job(
            api.get_device_with_template, device_id
        )
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}
        if PROP_LOCK_MODE in properties:
            entities.append(AlphaSmartCloudDeviceLock(api, device_data))

    async_add_entities(entities)


class AlphaSmartCloudDeviceLock(LockEntity):
    """Representation of an Alpha Smart Cloud device lock."""

    _attr_has_entity_name = True

    def __init__(self, api: AlphaSmartCloudAPI, device_data: dict[str, Any]) -> None:
        """Initialize the lock entity."""
        self._api = api
        self._device_id = device_data["deviceId"]
        self._attr_unique_id = f"{self._device_id}_lock"
        self._attr_name = "Control Lock"
        self._attr_is_locked = None
        self._lock_mode: dict[str, Any] = {}
        self._pending_lock: tuple[bool, float] | None = None

        device_info = device_data.get("deviceInfo", {})
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device_info.get("description", "Device"),
            manufacturer=device_info.get("oem"),
            model=device_info.get("type"),
        )

        self._update_from_data(device_data)

    def _is_locked_from_value(self, value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        return bool(value.get("menu")) or bool(value.get("targetTemp"))

    def _build_lock_payload(self, locked: bool) -> dict[str, bool]:
        payload = {
            "standby": False,
            "menu": locked,
            "targetTemp": locked,
            "reserved1": False,
            "reserved2": False,
            "reserved3": False,
            "reserved4": False,
            "reserved5": False,
        }
        for key, value in self._lock_mode.items():
            if key not in payload and isinstance(value, bool):
                payload[key] = value
        return payload

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}
        now = time.monotonic()

        if PROP_NAME in properties:
            self._attr_device_info["name"] = properties[PROP_NAME]["value"]

        if PROP_LOCK_MODE in properties:
            lock_mode = properties[PROP_LOCK_MODE]["value"]
            if isinstance(lock_mode, dict):
                self._lock_mode = lock_mode
            else:
                self._lock_mode = {}

            is_locked = self._is_locked_from_value(lock_mode)
            if self._pending_lock is not None:
                pending_val, timestamp = self._pending_lock
                if now - timestamp > 10 or is_locked == pending_val:
                    self._pending_lock = None
                else:
                    is_locked = pending_val

            self._attr_is_locked = is_locked

    async def async_update(self) -> None:
        """Fetch new state data for this device."""
        device_data = await self.hass.async_add_executor_job(
            self._api.get_device_with_template, self._device_id
        )
        self._update_from_data(device_data)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the device controls."""
        payload = self._build_lock_payload(True)
        self._pending_lock = (True, time.monotonic())

        try:
            await self.hass.async_add_executor_job(
                self._api.set_device_value, self._device_id, PROP_LOCK_MODE, payload
            )
        except Exception:
            self._pending_lock = None
            raise

        self._attr_is_locked = True
        self._lock_mode = payload
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the device controls."""
        payload = self._build_lock_payload(False)
        self._pending_lock = (False, time.monotonic())

        try:
            await self.hass.async_add_executor_job(
                self._api.set_device_value, self._device_id, PROP_LOCK_MODE, payload
            )
        except Exception:
            self._pending_lock = None
            raise

        self._attr_is_locked = False
        self._lock_mode = payload
        self.async_write_ha_state()
