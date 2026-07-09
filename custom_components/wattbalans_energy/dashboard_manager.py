"""Create and synchronize the WattBalans Lovelace dashboard."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from homeassistant.components import frontend
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.components.lovelace.const import (
    CONF_ICON,
    CONF_REQUIRE_ADMIN,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    LOVELACE_DATA,
    MODE_STORAGE,
)
from homeassistant.const import CONF_MODE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .dashboard import build_dashboard_config

_LOGGER = logging.getLogger(__name__)

DASHBOARD_TITLE = "WattBalans Energy"
DASHBOARD_URL_PATH = "wattbalans-energy"
DASHBOARD_ICON = "mdi:home-lightning-bolt"
_MANAGED_MARKER = "wattbalans_energy"
_MANAGED_VERSION = 3

ConfiguredEntities = Mapping[str, Sequence[str] | Mapping[str, str]]


def _dashboard_metadata() -> dict[str, Any]:
    """Return the Lovelace dashboard registry metadata."""
    return {
        CONF_ICON: DASHBOARD_ICON,
        CONF_REQUIRE_ADMIN: False,
        CONF_SHOW_IN_SIDEBAR: True,
        CONF_TITLE: DASHBOARD_TITLE,
        CONF_URL_PATH: DASHBOARD_URL_PATH,
        CONF_MODE: MODE_STORAGE,
    }


async def async_ensure_dashboard(
    hass: HomeAssistant,
    enabled_features: Iterable[str],
    configured_entities: ConfiguredEntities | None = None,
) -> bool:
    """Create or update the managed WattBalans dashboard."""
    if LOVELACE_DATA not in hass.data:
        _LOGGER.warning(
            "Lovelace is not available yet; WattBalans dashboard sync is skipped"
        )
        return False

    dashboard_item = await _async_ensure_dashboard_item(hass)
    if dashboard_item is None:
        return False

    _async_ensure_panel(hass, dashboard_item)

    lovelace_config = hass.data[LOVELACE_DATA].dashboards.get(DASHBOARD_URL_PATH)
    if lovelace_config is None:
        lovelace_config = lovelace_dashboard.LovelaceStorage(hass, dashboard_item)
        hass.data[LOVELACE_DATA].dashboards[DASHBOARD_URL_PATH] = lovelace_config

    current_config = await _async_load_dashboard_config(lovelace_config)
    if current_config is not None and not _is_managed_dashboard(current_config):
        _LOGGER.warning(
            "Dashboard %s already exists and is not managed by WattBalans; not overwriting it",
            DASHBOARD_URL_PATH,
        )
        return False

    entity_map = _entity_map_from_configured_entities(configured_entities or {})
    dashboard_config = build_dashboard_config(
        enabled_features,
        entity_map,
        _entity_metadata(hass, entity_map),
    )
    dashboard_config[_MANAGED_MARKER] = {
        "managed": True,
        "version": _MANAGED_VERSION,
    }

    await lovelace_config.async_save(dashboard_config)
    return True


async def _async_ensure_dashboard_item(hass: HomeAssistant) -> dict[str, Any] | None:
    """Ensure the WattBalans dashboard exists in Lovelace dashboard storage."""
    dashboards_collection = lovelace_dashboard.DashboardsCollection(hass)
    await dashboards_collection.async_load()

    for dashboard_item in dashboards_collection.async_items():
        if dashboard_item.get(CONF_URL_PATH) == DASHBOARD_URL_PATH:
            return dashboard_item

    try:
        return await dashboards_collection.async_create_item(_dashboard_metadata())
    except HomeAssistantError as err:
        _LOGGER.warning("Could not create WattBalans dashboard: %s", err)
        return None


async def _async_load_dashboard_config(lovelace_config: Any) -> dict[str, Any] | None:
    """Load existing dashboard configuration if it exists."""
    try:
        return await lovelace_config.async_load(False)
    except HomeAssistantError:
        return None


def _async_ensure_panel(hass: HomeAssistant, dashboard_item: dict[str, Any]) -> None:
    """Register the WattBalans dashboard in the Home Assistant sidebar."""
    frontend.async_register_built_in_panel(
        hass,
        "lovelace",
        frontend_url_path=DASHBOARD_URL_PATH,
        require_admin=dashboard_item.get(CONF_REQUIRE_ADMIN, False),
        show_in_sidebar=dashboard_item.get(CONF_SHOW_IN_SIDEBAR, True),
        sidebar_title=dashboard_item.get(CONF_TITLE, DASHBOARD_TITLE),
        sidebar_icon=dashboard_item.get(CONF_ICON, DASHBOARD_ICON),
        config={"mode": MODE_STORAGE},
        update=DASHBOARD_URL_PATH in hass.data[LOVELACE_DATA].dashboards,
    )


def _entity_map_from_configured_entities(
    configured_entities: ConfiguredEntities,
) -> dict[str, tuple[str, ...]]:
    """Convert configured entity selections to dashboard entity IDs per feature."""
    entity_map: dict[str, tuple[str, ...]] = {}

    for feature, configured in configured_entities.items():
        if isinstance(configured, Mapping):
            entity_ids = tuple(str(entity_id) for entity_id in configured.values() if entity_id)
        else:
            entity_ids = tuple(str(entity_id) for entity_id in configured if entity_id)

        if entity_ids:
            entity_map[feature] = entity_ids

    return entity_map


def _entity_metadata(
    hass: HomeAssistant,
    entity_map: Mapping[str, tuple[str, ...]],
) -> dict[str, dict[str, str | None]]:
    """Return dashboard metadata for configured entities."""
    metadata: dict[str, dict[str, str | None]] = {}

    for entity_ids in entity_map.values():
        for entity_id in entity_ids:
            state = hass.states.get(entity_id)
            domain = entity_id.split(".", 1)[0]
            metadata[entity_id] = {
                "device_class": state.attributes.get("device_class") if state else None,
                "domain": domain,
                "friendly_name": state.attributes.get("friendly_name") if state else None,
                "state_class": state.attributes.get("state_class") if state else None,
                "unit": state.attributes.get("unit_of_measurement") if state else None,
            }

    return metadata


def _is_managed_dashboard(config: dict[str, Any]) -> bool:
    """Return whether the existing dashboard is managed by WattBalans."""
    marker = config.get(_MANAGED_MARKER)
    return isinstance(marker, dict) and marker.get("managed") is True
