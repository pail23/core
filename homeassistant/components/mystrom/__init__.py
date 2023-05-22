"""The myStrom integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from pymystrom.bulb import MyStromBulb
from pymystrom.exceptions import MyStromConnectionError
from pymystrom.switch import MyStromSwitch
from pymystrom import get_device_info

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up myStrom from a config entry."""
    host = entry.data[CONF_HOST]
    device = None
    try:
        info = await get_device_info(host)
    except MyStromConnectionError as err:
        _LOGGER.error("No route to myStrom plug: %s", host)
        raise ConfigEntryNotReady() from err

    device_type = info["type"]
    if device_type in [101, 106, 107]:
        device = MyStromSwitch(host)
    elif device_type == 102:
        mac = info["mac"]
        device = MyStromBulb(host, mac)
        if device.bulb_type not in ["rgblamp", "strip"]:
            _LOGGER.error(
                "Device %s (%s) is not a myStrom bulb nor myStrom LED Strip",
                host,
                mac,
            )
            return False
    else:
        _LOGGER.error("Unsupported myStrom device type: %s", device_type)
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "device": device,
        "info": info,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
