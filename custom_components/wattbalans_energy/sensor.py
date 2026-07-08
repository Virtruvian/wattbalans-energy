"""Diagnostic sensors for WattBalans Energy Management."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_FEATURES, DOMAIN, NAME


@dataclass(frozen=True, kw_only=True)
class WattBalansFeatureSensorDescription(SensorEntityDescription):
    """Describe a WattBalans feature-status sensor."""

    feature: str


FEATURE_DESCRIPTIONS: dict[str, WattBalansFeatureSensorDescription] = {
    "solar": WattBalansFeatureSensorDescription(
        key="solar",
        translation_key="solar_module",
        feature="solar",
        icon="mdi:solar-power",
    ),
    "grid": WattBalansFeatureSensorDescription(
        key="grid",
        translation_key="grid_module",
        feature="grid",
        icon="mdi:transmission-tower",
    ),
    "battery": WattBalansFeatureSensorDescription(
        key="battery",
        translation_key="battery_module",
        feature="battery",
        icon="mdi:home-battery",
    ),
    "ev_charging": WattBalansFeatureSensorDescription(
        key="ev_charging",
        translation_key="ev_charging_module",
        feature="ev_charging",
        icon="mdi:ev-station",
    ),
    "dynamic_tariff": WattBalansFeatureSensorDescription(
        key="dynamic_tariff",
        translation_key="dynamic_tariff_module",
        feature="dynamic_tariff",
        icon="mdi:currency-eur",
    ),
    "controllable_loads": WattBalansFeatureSensorDescription(
        key="controllable_loads",
        translation_key="controllable_loads_module",
        feature="controllable_loads",
        icon="mdi:power-plug",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up diagnostic sensors for enabled WattBalans modules."""
    enabled_features: tuple[str, ...] = hass.data[DOMAIN][entry.entry_id][CONF_FEATURES]

    async_add_entities(
        WattBalansFeatureSensor(entry, FEATURE_DESCRIPTIONS[feature])
        for feature in enabled_features
        if feature in FEATURE_DESCRIPTIONS
    )


class WattBalansFeatureSensor(SensorEntity):
    """Represent whether a WattBalans module is enabled."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_native_value = "enabled"

    def __init__(
        self,
        entry: ConfigEntry,
        description: WattBalansFeatureSensorDescription,
    ) -> None:
        """Initialize a WattBalans feature-status sensor."""
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.feature}_module"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="WattBalans",
            model="Energy Management",
        )
