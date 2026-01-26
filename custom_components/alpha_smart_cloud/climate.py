"""Support for Alpha Smart Cloud climate devices."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .const import (
    DOMAIN,
    PROP_CURRENT_TEMPERATURE,
    PROP_FIRMWARE,
    PROP_HUMIDITY,
    PROP_NAME,
    PROP_SERIAL_NO,
    PROP_TARGET_TEMPERATURE,
    PROP_TIME_PROFILE,
    PROP_WORK_MODE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud climate devices."""
    api = entry.runtime_data

    # Fetch devices directly
    devices_data = await hass.async_add_executor_job(api.get_devices)

    entities = []
    for device in devices_data:
        if device.get("type") == "rbg":
            device_id = device["deviceId"]
            device_data = await hass.async_add_executor_job(
                api.get_device_with_template, device_id
            )
            entities.append(AlphaSmartCloudClimate(api, device_data))

    async_add_entities(entities)


class AlphaSmartCloudClimate(ClimateEntity):
    """Representation of an Alpha Smart Cloud climate device."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.AUTO, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_precision = PRECISION_TENTHS

    def __init__(self, api: AlphaSmartCloudAPI, device_data: dict[str, Any]) -> None:
        """Initialize the climate device."""
        self._api = api
        self._device_id = device_data["deviceId"]
        self._attr_unique_id = self._device_id
        self._attr_target_temperature = None
        self._attr_hvac_mode = None
        self._attr_current_temperature = None
        self._attr_current_humidity = None
        self._attr_extra_state_attributes = {}
        self._pending_updates: dict[str, tuple[Any, float]] = {}

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
        now = time.monotonic()

        if PROP_NAME in properties:
            self._attr_device_info["name"] = properties[PROP_NAME]["value"]

        if PROP_TARGET_TEMPERATURE in properties:
            prop = properties[PROP_TARGET_TEMPERATURE]
            target_temp = float(prop["value"])

            if PROP_TARGET_TEMPERATURE in self._pending_updates:
                pending_val, timestamp = self._pending_updates[PROP_TARGET_TEMPERATURE]
                if now - timestamp > 10 or target_temp == pending_val:
                    del self._pending_updates[PROP_TARGET_TEMPERATURE]
                else:
                    target_temp = pending_val

            self._attr_target_temperature = target_temp

            # Update bounds and step from template metadata
            metadata = prop.get("properties", {})
            if "min" in metadata:
                self._attr_min_temp = float(metadata["min"])
            if "max" in metadata:
                self._attr_max_temp = float(metadata["max"])
            if "step" in metadata:
                self._attr_target_temperature_step = float(metadata["step"])

        if PROP_CURRENT_TEMPERATURE in properties:
            self._attr_current_temperature = float(
                properties[PROP_CURRENT_TEMPERATURE]["value"]
            )

        if PROP_HUMIDITY in properties:
            self._attr_current_humidity = float(properties[PROP_HUMIDITY]["value"])

        if PROP_WORK_MODE in properties:
            work_mode = properties[PROP_WORK_MODE]["value"]

            if PROP_WORK_MODE in self._pending_updates:
                pending_val, timestamp = self._pending_updates[PROP_WORK_MODE]
                if now - timestamp > 10 or work_mode == pending_val:
                    del self._pending_updates[PROP_WORK_MODE]
                else:
                    work_mode = pending_val

            if work_mode == "auto":
                self._attr_hvac_mode = HVACMode.AUTO
            elif work_mode == "manual":
                self._attr_hvac_mode = HVACMode.HEAT
            else:
                self._attr_hvac_mode = HVACMode.HEAT

        # Update firmware version and serial number in device info if available
        if PROP_FIRMWARE in properties:
            firmware_info = properties[PROP_FIRMWARE]["value"]
            if isinstance(firmware_info, dict) and "current" in firmware_info:
                self._attr_device_info["sw_version"] = firmware_info["current"]

        if PROP_SERIAL_NO in properties:
            self._attr_device_info["serial_number"] = properties[PROP_SERIAL_NO][
                "value"
            ]

        if PROP_TIME_PROFILE in properties:
            self._attr_extra_state_attributes["time_profile"] = properties[
                PROP_TIME_PROFILE
            ]["value"]
        else:
            self._attr_extra_state_attributes.pop("time_profile", None)

        # Heuristic for OFF if target temp is very low and it's in manual
        if (
            self._attr_hvac_mode == HVACMode.HEAT
            and self._attr_target_temperature is not None
            and self._attr_target_temperature <= 5.0
        ):
            self._attr_hvac_mode = HVACMode.OFF

    async def async_update(self) -> None:
        """Fetch new state data for this device."""
        device_data = await self.hass.async_add_executor_job(
            self._api.get_device_with_template, self._device_id
        )
        self._update_from_data(device_data)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        # Clamp value to allowed range
        if self.min_temp is not None and temp < self.min_temp:
            temp = self.min_temp
        if self.max_temp is not None and temp > self.max_temp:
            temp = self.max_temp

        self._pending_updates[PROP_TARGET_TEMPERATURE] = (temp, time.monotonic())

        try:
            await self.hass.async_add_executor_job(
                self._api.set_device_value,
                self._device_id,
                PROP_TARGET_TEMPERATURE,
                temp,
            )
        except Exception:
            if PROP_TARGET_TEMPERATURE in self._pending_updates:
                del self._pending_updates[PROP_TARGET_TEMPERATURE]
            raise

        self._attr_target_temperature = temp
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            # Set to manual and low temperature
            self._pending_updates[PROP_WORK_MODE] = ("manual", time.monotonic())
            try:
                await self.hass.async_add_executor_job(
                    self._api.set_device_value,
                    self._device_id,
                    PROP_WORK_MODE,
                    "manual",
                )
            except Exception:
                if PROP_WORK_MODE in self._pending_updates:
                    del self._pending_updates[PROP_WORK_MODE]
                raise
            await self.async_set_temperature(**{ATTR_TEMPERATURE: 5.0})
        elif hvac_mode == HVACMode.AUTO:
            self._pending_updates[PROP_WORK_MODE] = ("auto", time.monotonic())
            try:
                await self.hass.async_add_executor_job(
                    self._api.set_device_value, self._device_id, PROP_WORK_MODE, "auto"
                )
            except Exception:
                if PROP_WORK_MODE in self._pending_updates:
                    del self._pending_updates[PROP_WORK_MODE]
                raise
        elif hvac_mode == HVACMode.HEAT:
            self._pending_updates[PROP_WORK_MODE] = ("manual", time.monotonic())
            try:
                await self.hass.async_add_executor_job(
                    self._api.set_device_value,
                    self._device_id,
                    PROP_WORK_MODE,
                    "manual",
                )
            except Exception:
                if PROP_WORK_MODE in self._pending_updates:
                    del self._pending_updates[PROP_WORK_MODE]
                raise
            if self._attr_target_temperature and self._attr_target_temperature <= 5.0:
                await self.async_set_temperature(**{ATTR_TEMPERATURE: 20.0})

        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()
