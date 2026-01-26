"""Support for Alpha Smart Cloud climate devices."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    PRESET_AWAY,
    PRESET_NONE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_TENTHS,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AlphaSmartCloudConfigEntry
from .api import AlphaSmartCloudAPI
from .coordinator import AlphaSmartCloudData, AlphaSmartCloudDataUpdateCoordinator
from .const import (
    DOMAIN,
    PROP_COOL_HEAT_MODE,
    PROP_CURRENT_TEMPERATURE,
    PROP_FIRMWARE,
    PROP_HUMIDITY,
    PROP_IS_ONLINE,
    PROP_NAME,
    PROP_SERIAL_NO,
    PROP_TARGET_TEMPERATURE,
    PROP_TIME_PROFILE,
    PROP_VACATION_MODE,
    PROP_VACATION_TEMPERATURE,
    PROP_WORK_MODE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlphaSmartCloudConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Alpha Smart Cloud climate devices."""
    api = entry.runtime_data.api
    coordinator = entry.runtime_data.coordinator

    devices_data = coordinator.data.devices
    group_names = coordinator.data.group_names

    entities = []
    for device in devices_data:
        if device.get("type") == "rbg":
            device_id = device["deviceId"]
            group_id = device.get("groupId")
            room_name = group_names.get(group_id)

            device_data = coordinator.data.device_data.get(device_id)
            if device_data:
                entities.append(
                    AlphaSmartCloudClimate(coordinator, api, device_data, room_name)
                )

    async_add_entities(entities)


class AlphaSmartCloudClimate(
    CoordinatorEntity[AlphaSmartCloudDataUpdateCoordinator], ClimateEntity
):
    """Representation of an Alpha Smart Cloud climate device."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_precision = PRECISION_TENTHS

    def __init__(
        self,
        coordinator: AlphaSmartCloudDataUpdateCoordinator,
        api: AlphaSmartCloudAPI,
        device_data: dict[str, Any],
        room_name: str | None = None,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._api = api
        self._device_id = device_data["deviceId"]
        self._attr_unique_id = self._device_id
        self._attr_target_temperature = None
        self._attr_preset_mode = PRESET_NONE
        self._attr_hvac_mode = None
        self._attr_hvac_action = None
        self._attr_current_temperature = None
        self._attr_current_humidity = None
        self._attr_available = False
        self._attr_extra_state_attributes = {}
        self._pending_updates: dict[str, tuple[Any, float]] = {}

        # Device info initialization
        device_info = device_data.get("deviceInfo", {})
        model = device_info.get("type")
        name = room_name or device_info.get("description", "Climate")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=name,
            manufacturer=device_info.get("oem"),
            model=model,
        )

        self._update_from_data(device_data)

    def _update_from_data(self, device_data: dict[str, Any]) -> None:
        """Update entity state from enriched device data."""
        properties = {prop["id"]: prop for prop in device_data.get("properties", [])}
        now = time.monotonic()

        # Check device availability - default to False if not present
        if PROP_IS_ONLINE in properties:
            self._attr_available = bool(properties[PROP_IS_ONLINE]["value"])
        else:
            self._attr_available = False
            _LOGGER.debug("Device %s missing online status, marking unavailable", self._device_id)

        if PROP_NAME in properties:
            self._attr_device_info["name"] = properties[PROP_NAME]["value"]

        # Vacation mode
        vacation_mode = False
        if PROP_VACATION_MODE in properties:
            vacation_mode_val = properties[PROP_VACATION_MODE]["value"]
            vacation_mode = vacation_mode_val == "on"
            self._attr_preset_mode = PRESET_AWAY if vacation_mode else PRESET_NONE
            self._attr_extra_state_attributes["vacation_mode"] = vacation_mode_val
        else:
            self._attr_preset_mode = PRESET_NONE

        if PROP_TARGET_TEMPERATURE in properties:
            prop = properties[PROP_TARGET_TEMPERATURE]
            target_temp = float(prop["value"])

            if PROP_TARGET_TEMPERATURE in self._pending_updates:
                pending_val, timestamp = self._pending_updates[PROP_TARGET_TEMPERATURE]
                if now - timestamp > 10 or target_temp == pending_val:
                    del self._pending_updates[PROP_TARGET_TEMPERATURE]
                else:
                    target_temp = pending_val

            if not vacation_mode:
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

        hvac_mode = HVACMode.HEAT
        if PROP_WORK_MODE in properties:
            work_mode = properties[PROP_WORK_MODE]["value"]

            if PROP_WORK_MODE in self._pending_updates:
                pending_val, timestamp = self._pending_updates[PROP_WORK_MODE]
                if now - timestamp > 10 or work_mode == pending_val:
                    del self._pending_updates[PROP_WORK_MODE]
                else:
                    work_mode = pending_val

            if work_mode == "auto":
                hvac_mode = HVACMode.AUTO
            elif work_mode == "manual":
                hvac_mode = HVACMode.HEAT

        if PROP_COOL_HEAT_MODE in properties:
            cool_heat_mode = properties[PROP_COOL_HEAT_MODE]["value"]
            if cool_heat_mode == "cool":
                if hvac_mode == HVACMode.HEAT:
                    hvac_mode = HVACMode.COOL
                self._attr_hvac_modes = [
                    HVACMode.COOL,
                    HVACMode.AUTO,
                    HVACMode.OFF,
                ]
            else:
                self._attr_hvac_modes = [
                    HVACMode.HEAT,
                    HVACMode.AUTO,
                    HVACMode.OFF,
                ]
        else:
            # Check aswRbgInfo for cooling support
            asw_rbg_info = properties.get("aswRbgInfo", {}).get("value", {})
            if isinstance(asw_rbg_info, dict) and asw_rbg_info.get("coolingProfile"):
                self._attr_hvac_modes = [
                    HVACMode.HEAT,
                    HVACMode.COOL,
                    HVACMode.AUTO,
                    HVACMode.OFF,
                ]
            else:
                self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.AUTO, HVACMode.OFF]

        self._attr_hvac_mode = hvac_mode

        if PROP_VACATION_TEMPERATURE in properties:
            vac_temp = float(properties[PROP_VACATION_TEMPERATURE]["value"])
            self._attr_extra_state_attributes["vacation_temperature"] = vac_temp
            if vacation_mode:
                self._attr_target_temperature = vac_temp
        else:
            self._attr_extra_state_attributes.pop("vacation_temperature", None)

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

    @callback
    def _handle_coordinator_update(self) -> None:
        device_data = self.coordinator.data.device_data.get(self._device_id)
        if device_data:
            self._update_from_data(device_data)
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        # Clamp value to allowed range
        if self.min_temp is not None and temp < self.min_temp:
            temp = self.min_temp
        if self.max_temp is not None and temp > self.max_temp:
            temp = self.max_temp

        # Round to step if available
        if self.target_temperature_step is not None:
            temp = (
                round(temp / self.target_temperature_step)
                * self.target_temperature_step
            )

        # If vacation mode is active, set vacation temperature instead
        if self._attr_preset_mode == PRESET_AWAY:
            property_id = PROP_VACATION_TEMPERATURE
        else:
            property_id = PROP_TARGET_TEMPERATURE

        _LOGGER.debug(
            "Setting temperature for device %s: %s = %.1f°C",
            self._device_id,
            property_id,
            temp,
        )

        self._pending_updates[property_id] = (temp, time.monotonic())

        try:
            await self.hass.async_add_executor_job(
                self._api.set_device_value,
                self._device_id,
                property_id,
                temp,
            )
            _LOGGER.debug(
                "Successfully set temperature for device %s to %.1f°C",
                self._device_id,
                temp,
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set temperature for device %s to %.1f°C: %s",
                self._device_id,
                temp,
                err,
            )
            if property_id in self._pending_updates:
                del self._pending_updates[property_id]
            raise

        self._attr_target_temperature = temp
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug("Setting HVAC mode for device %s to %s", self._device_id, hvac_mode)

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
                _LOGGER.debug("Set device %s to manual mode for OFF", self._device_id)
            except Exception as err:
                _LOGGER.error(
                    "Failed to set device %s to manual mode: %s",
                    self._device_id,
                    err,
                )
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
                _LOGGER.debug("Set device %s to auto mode", self._device_id)
            except Exception as err:
                _LOGGER.error(
                    "Failed to set device %s to auto mode: %s",
                    self._device_id,
                    err,
                )
                if PROP_WORK_MODE in self._pending_updates:
                    del self._pending_updates[PROP_WORK_MODE]
                raise
        elif hvac_mode in (HVACMode.HEAT, HVACMode.COOL):
            self._pending_updates[PROP_WORK_MODE] = ("manual", time.monotonic())
            try:
                await self.hass.async_add_executor_job(
                    self._api.set_device_value,
                    self._device_id,
                    PROP_WORK_MODE,
                    "manual",
                )
                _LOGGER.debug("Set device %s to manual mode for %s", self._device_id, hvac_mode)
            except Exception as err:
                _LOGGER.error(
                    "Failed to set device %s to manual mode: %s",
                    self._device_id,
                    err,
                )
                if PROP_WORK_MODE in self._pending_updates:
                    del self._pending_updates[PROP_WORK_MODE]
                raise
            if self._attr_target_temperature and self._attr_target_temperature <= 5.0:
                await self.async_set_temperature(**{ATTR_TEMPERATURE: 20.0})

        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()
