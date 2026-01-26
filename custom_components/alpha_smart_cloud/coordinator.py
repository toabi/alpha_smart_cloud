"""DataUpdateCoordinator for Alpha Smart Cloud."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AlphaSmartCloudAPI,
    AlphaSmartCloudAuthError,
    AlphaSmartCloudConnectionError,
)
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class AlphaSmartCloudData:
    """Container for coordinator data."""

    devices: list[dict[str, Any]]
    device_data: dict[str, dict[str, Any]]
    homes: list[dict[str, Any]]
    group_names: dict[str, str]


class AlphaSmartCloudDataUpdateCoordinator(DataUpdateCoordinator[AlphaSmartCloudData]):
    """Coordinator for Alpha Smart Cloud data."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, api: AlphaSmartCloudAPI
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
            config_entry=config_entry,
        )
        self.api = api
        self._device_templates: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> AlphaSmartCloudData:
        """Fetch data from API."""
        _LOGGER.debug("Starting data update")

        try:
            devices = await self.hass.async_add_executor_job(self.api.get_devices)
            _LOGGER.debug("Fetched %d devices", len(devices))
        except AlphaSmartCloudAuthError as err:
            _LOGGER.error("Authentication failed while fetching devices: %s", err)
            raise ConfigEntryAuthFailed from err
        except AlphaSmartCloudConnectionError as err:
            _LOGGER.warning("Connection error while fetching devices: %s", err)
            raise UpdateFailed("Failed to fetch devices or homes") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching devices: %s", err)
            raise UpdateFailed("Unexpected error fetching devices or homes") from err

        try:
            homes = await self.hass.async_add_executor_job(self.api.get_homes)
            _LOGGER.debug("Fetched %d homes", len(homes))
        except AlphaSmartCloudAuthError as err:
            _LOGGER.error("Authentication failed while fetching homes: %s", err)
            raise ConfigEntryAuthFailed from err
        except AlphaSmartCloudConnectionError as err:
            _LOGGER.warning("Connection error while fetching homes: %s", err)
            raise UpdateFailed("Failed to fetch devices or homes") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching homes: %s", err)
            raise UpdateFailed("Unexpected error fetching devices or homes") from err

        group_names = _build_group_names(homes)

        device_data: dict[str, dict[str, Any]] = {}
        failed_devices: list[str] = []

        for device in devices:
            device_id = device["deviceId"]
            try:
                # Fetch device values
                values = await self.hass.async_add_executor_job(
                    self.api.get_device_values, device_id
                )

                # Fetch template only if not cached
                if device_id not in self._device_templates:
                    _LOGGER.debug("Fetching template for device %s (not cached)", device_id)
                    template = await self.hass.async_add_executor_job(
                        self.api.get_device_template, device_id
                    )
                    self._device_templates[device_id] = template
                else:
                    template = self._device_templates[device_id]

                # Build enriched device data using cached template
                device_data[device_id] = self._enrich_device_data(
                    device_id, values, template
                )

            except AlphaSmartCloudAuthError as err:
                _LOGGER.error("Authentication failed while fetching device %s: %s", device_id, err)
                raise ConfigEntryAuthFailed from err
            except AlphaSmartCloudConnectionError as err:
                _LOGGER.warning("Connection error while fetching device %s: %s", device_id, err)
                failed_devices.append(device_id)
                continue
            except Exception as err:
                _LOGGER.exception("Unexpected error fetching device %s: %s", device_id, err)
                failed_devices.append(device_id)
                continue

        if failed_devices:
            _LOGGER.warning(
                "Failed to fetch data for %d device(s): %s",
                len(failed_devices),
                ", ".join(failed_devices),
            )

        if not device_data and devices:
            _LOGGER.error("Failed to fetch data for all devices")
            raise UpdateFailed("Failed to fetch device details for all devices")

        _LOGGER.debug("Update completed successfully with %d devices", len(device_data))
        return AlphaSmartCloudData(
            devices=devices,
            device_data=device_data,
            homes=homes,
            group_names=group_names,
        )

    def _enrich_device_data(
        self, device_id: str, values: dict[str, Any], template: dict[str, Any]
    ) -> dict[str, Any]:
        """Enrich device values with template metadata."""
        element_map = {}
        for shadow in template.get("shadows", []):
            shadow_name = shadow.get("name")
            shadow_category = shadow.get("category")
            for element in shadow.get("elements", []):
                element_id = element.get("id")
                element_map[element_id] = {
                    "shadow": shadow_name,
                    "shadowCategory": shadow_category,
                    "category": element.get("content", {}).get("category"),
                    "properties": element.get("content", {}).get("properties", {}),
                    "writable": element.get("writable", False),
                    "userWritable": element.get("userWritable"),
                    "disabled": element.get("disabled"),
                    "installationOnly": element.get("installationOnly"),
                }

        enriched_values = []
        for key, value in values.items():
            metadata = element_map.get(key, {})
            enriched_values.append(
                {
                    "id": key,
                    "value": value,
                    "category": metadata.get("category", "unknown"),
                    "shadow": metadata.get("shadow", "unknown"),
                    "writable": metadata.get("writable", False),
                    "userWritable": metadata.get("userWritable"),
                    "properties": metadata.get("properties", {}),
                }
            )

        device_type = template.get("type")
        if device_type == "rbg":
            device_type = "Raumbediengerät"

        return {
            "deviceId": device_id,
            "deviceInfo": {
                "oem": template.get("oem"),
                "type": device_type,
                "description": template.get("description"),
                "gtin": template.get("gtin"),
            },
            "properties": enriched_values,
            "rawTemplate": template,
        }


def _build_group_names(homes: list[dict[str, Any]]) -> dict[str, str]:
    group_names: dict[str, str] = {}
    for home in homes:
        for group in home.get("groups", []):
            name = group.get("name")
            if name:
                group_names[group["id"]] = name
    return group_names
