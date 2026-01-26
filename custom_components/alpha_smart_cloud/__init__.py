"""The Alpha Smart Cloud integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .api import AlphaSmartCloudAPI
from .const import (
    ALPHA_SMART_API_ID,
    ALPHA_SMART_CLIENT_ID,
    ALPHA_SMART_IDENTITY_POOL_ID,
    ALPHA_SMART_REGION,
    ALPHA_SMART_USER_POOL_ID,
)

_PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]

type AlphaSmartCloudConfigEntry = ConfigEntry[AlphaSmartCloudAPI]


async def async_setup_entry(
    hass: HomeAssistant, entry: AlphaSmartCloudConfigEntry
) -> bool:
    """Set up Alpha Smart Cloud from a config entry."""

    api = AlphaSmartCloudAPI(
        region=ALPHA_SMART_REGION,
        user_pool_id=ALPHA_SMART_USER_POOL_ID,
        client_id=ALPHA_SMART_CLIENT_ID,
        identity_pool_id=ALPHA_SMART_IDENTITY_POOL_ID,
        api_id=ALPHA_SMART_API_ID,
    )

    if not await hass.async_add_executor_job(
        api.authenticate, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    ):
        return False

    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AlphaSmartCloudConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
