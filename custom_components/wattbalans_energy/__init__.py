"""WattBalans Energy Management integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ENTITIES, CONF_FEATURES, DEFAULT_FEATURES, DOMAIN
from .dashboard_manager import async_ensure_dashboard

PLATFORMS: tuple[Platform, ...] = (Platform.SENSOR,)

type WattBalansConfigEntry = ConfigEntry


def _enabled_features(entry: WattBalansConfigEntry) -> tuple[str, ...]:
    """Return the enabled WattBalans features for a config entry."""
    configured = entry.options.get(
        CONF_FEATURES,
        entry.data.get(CONF_FEATURES, DEFAULT_FEATURES),
    )
    return tuple(feature for feature, enabled in configured.items() if enabled)


def _configured_entities(entry: WattBalansConfigEntry) -> dict[str, dict[str, str]]:
    """Return configured WattBalans entity IDs for a config entry."""
    return entry.options.get(
        CONF_ENTITIES,
        entry.data.get(CONF_ENTITIES, {}),
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattBalansConfigEntry,
) -> bool:
    """Set up WattBalans Energy Management from a config entry."""
    enabled_features = _enabled_features(entry)
    configured_entities = _configured_entities(entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_ENTITIES: configured_entities,
        CONF_FEATURES: enabled_features,
    }

    if enabled_features:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await async_ensure_dashboard(hass, enabled_features, configured_entities)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: WattBalansConfigEntry,
) -> bool:
    """Unload a WattBalans Energy Management config entry."""
    enabled_features = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get(
        CONF_FEATURES,
        (),
    )

    unload_ok = True
    if enabled_features:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if not hass.data.get(DOMAIN):
            hass.data.pop(DOMAIN, None)

    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant,
    entry: WattBalansConfigEntry,
) -> None:
    """Reload the integration when component options change."""
    await hass.config_entries.async_reload(entry.entry_id)
