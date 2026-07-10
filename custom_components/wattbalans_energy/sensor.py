"""Sensors for WattBalans Energy Management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ENTITIES, CONF_FEATURES, DOMAIN, NAME
from .naming import entity_group, friendly_label, metadata_from_state


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

FEATURE_ICONS = {
    "solar": "mdi:solar-power",
    "grid": "mdi:transmission-tower",
    "battery": "mdi:home-battery",
    "ev_charging": "mdi:ev-station",
    "dynamic_tariff": "mdi:currency-eur",
    "controllable_loads": "mdi:power-plug",
}

GROUP_ICONS = {
    "soc": "mdi:battery-heart",
    "power": "mdi:flash",
    "energy": "mdi:counter",
    "price": "mdi:currency-eur",
    "control": "mdi:toggle-switch",
    "other": "mdi:chart-line",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for enabled WattBalans modules and selected sources."""
    enabled_features: tuple[str, ...] = hass.data[DOMAIN][entry.entry_id][CONF_FEATURES]
    configured_entities: dict[str, Any] = hass.data[DOMAIN][entry.entry_id].get(CONF_ENTITIES, {})

    entities: list[SensorEntity] = [
        WattBalansFeatureSensor(entry, FEATURE_DESCRIPTIONS[feature])
        for feature in enabled_features
        if feature in FEATURE_DESCRIPTIONS
    ]

    for feature in enabled_features:
        for source_entity_id in _feature_entity_ids(configured_entities.get(feature, [])):
            entities.append(WattBalansSourceSensor(hass, entry, feature, source_entity_id))

    async_add_entities(entities)


def _feature_entity_ids(value: Any) -> tuple[str, ...]:
    """Normalize configured feature entity IDs."""
    if isinstance(value, dict):
        value = value.values()
    if isinstance(value, str):
        value = [value]
    if not value:
        return ()
    return tuple(str(entity_id) for entity_id in value if entity_id)


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


class WattBalansSourceSensor(SensorEntity):
    """Mirror a selected Home Assistant source entity with a WattBalans name."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        feature: str,
        source_entity_id: str,
    ) -> None:
        """Initialize the source mirror sensor."""
        self._hass = hass
        self._feature = feature
        self._source_entity_id = source_entity_id
        self._attr_unique_id = f"{entry.entry_id}_{feature}_{source_entity_id.replace('.', '_')}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="WattBalans",
            model="Energy Management",
        )
        self._update_from_source()

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return metadata linking this entity to the original source."""
        return {
            "source_entity_id": self._source_entity_id,
            "wattbalans_feature": self._feature,
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to source entity updates."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source_entity_id],
                self._async_source_changed,
            )
        )

    @callback
    def _async_source_changed(self, event: Event[Any]) -> None:
        """Handle source entity state changes."""
        self._update_from_source()
        self.async_write_ha_state()

    def _update_from_source(self) -> None:
        """Copy state and metadata from the source entity."""
        state = self._hass.states.get(self._source_entity_id)
        metadata = metadata_from_state(self._source_entity_id, state)
        label = friendly_label(self._source_entity_id, metadata)
        group = entity_group(self._source_entity_id, metadata)

        self._attr_name = f"WattBalans {label}"
        self._attr_icon = GROUP_ICONS.get(group, FEATURE_ICONS.get(self._feature, "mdi:chart-line"))

        if state is None:
            self._attr_native_value = None
            self._attr_native_unit_of_measurement = None
            self._attr_device_class = None
            self._attr_state_class = None
            return

        self._attr_native_value = state.state
        self._attr_native_unit_of_measurement = state.attributes.get("unit_of_measurement")
        self._attr_device_class = state.attributes.get("device_class")
        self._attr_state_class = state.attributes.get("state_class")
