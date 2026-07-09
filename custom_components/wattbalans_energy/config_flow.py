"""Config flow for WattBalans Energy Management."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er, selector

from .const import (
    CONF_ENTITIES,
    CONF_FEATURES,
    DEFAULT_FEATURES,
    DOMAIN,
    FEATURE_BATTERY,
    FEATURE_CONTROLLABLE_LOADS,
    FEATURE_DYNAMIC_TARIFF,
    FEATURE_EV_CHARGING,
    FEATURE_GRID,
    FEATURE_SOLAR,
)

FEATURE_KEYS = (
    FEATURE_SOLAR,
    FEATURE_GRID,
    FEATURE_BATTERY,
    FEATURE_EV_CHARGING,
    FEATURE_DYNAMIC_TARIFF,
    FEATURE_CONTROLLABLE_LOADS,
)

ENTITY_FIELDS: dict[str, str] = {
    FEATURE_SOLAR: "solar_entities",
    FEATURE_GRID: "grid_entities",
    FEATURE_BATTERY: "battery_entities",
    FEATURE_EV_CHARGING: "ev_charging_entities",
    FEATURE_DYNAMIC_TARIFF: "dynamic_tariff_entities",
    FEATURE_CONTROLLABLE_LOADS: "controllable_loads_entities",
}

_AUTO_DETECT_KEYWORDS: dict[str, tuple[str, ...]] = {
    FEATURE_SOLAR: ("solar", "zonne", "pv", "panel", "omvormer", "inverter"),
    FEATURE_GRID: ("grid", "net", "p1", "meter", "import", "export", "afname", "teruglever"),
    FEATURE_BATTERY: ("battery", "batterij", "accu", "soc", "charge", "discharge"),
    FEATURE_EV_CHARGING: ("ev", "laad", "charger", "charging", "auto"),
    FEATURE_DYNAMIC_TARIFF: ("tariff", "tarief", "prijs", "price", "tibber", "dynamic"),
    FEATURE_CONTROLLABLE_LOADS: ("plug", "stekker", "switch", "schakel", "load", "verbruiker"),
}

_AUTO_DETECT_MIN_SCORE: dict[str, int] = {
    FEATURE_SOLAR: 4,
    FEATURE_GRID: 4,
    FEATURE_BATTERY: 5,
    FEATURE_EV_CHARGING: 4,
    FEATURE_DYNAMIC_TARIFF: 4,
    FEATURE_CONTROLLABLE_LOADS: 4,
}

_BATTERY_STORAGE_KEYWORDS = (
    "alpha ess",
    "alpha_ess",
    "alphaess",
    "ess",
    "zinvolt",
    "thuisaccu",
    "home battery",
    "battery soc",
    "batterij soc",
    "soc",
    "state of charge",
    "charge",
    "discharge",
    "laadvermogen",
    "ontlaadvermogen",
    "battery power",
    "accu vermogen",
    "energy storage",
    "omvormer",
    "inverter",
)

_SMALL_BATTERY_KEYWORDS = (
    "dimmer",
    "remote",
    "afstandsbediening",
    "button",
    "knop",
    "nuki",
    "bridge",
    "motion",
    "beweging",
    "door",
    "deur",
    "window",
    "raam",
    "sensor keuken",
    "entree-sensor",
    "w-dimmer",
    "k-dimmer",
)

_POWER_UNITS = {UnitOfPower.WATT, UnitOfPower.KILO_WATT}
_ENERGY_UNITS = {UnitOfEnergy.WATT_HOUR, UnitOfEnergy.KILO_WATT_HOUR}


def _feature_schema(current: dict[str, bool]) -> vol.Schema:
    """Build the feature selection schema."""
    return vol.Schema(
        {
            vol.Required(
                feature,
                default=current.get(feature, DEFAULT_FEATURES[feature]),
            ): bool
            for feature in FEATURE_KEYS
        }
    )


def _entity_schema(
    enabled_features: dict[str, bool],
    current_entities: dict[str, list[str]],
    auto_detected_entities: dict[str, list[str]],
) -> vol.Schema:
    """Build the entity selection schema for selected features."""
    schema: dict[vol.Optional, selector.EntitySelector] = {}

    for feature in FEATURE_KEYS:
        if not enabled_features.get(feature, False):
            continue

        field = ENTITY_FIELDS[feature]
        current = current_entities.get(feature)
        default = current if current is not None else auto_detected_entities.get(feature, [])

        schema[vol.Optional(field, default=default)] = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["sensor", "binary_sensor", "switch"],
                multiple=True,
            )
        )

    return vol.Schema(schema)


def _features_from_input(user_input: dict[str, Any]) -> dict[str, bool]:
    """Normalize selected features from form input."""
    return {feature: bool(user_input[feature]) for feature in FEATURE_KEYS}


def _entities_from_input(
    enabled_features: dict[str, bool],
    user_input: dict[str, Any],
) -> dict[str, list[str]]:
    """Normalize selected Home Assistant entities from form input."""
    entities: dict[str, list[str]] = {}

    for feature in FEATURE_KEYS:
        if not enabled_features.get(feature, False):
            continue

        selected = _normalize_entity_list(user_input.get(ENTITY_FIELDS[feature], []))
        if selected:
            entities[feature] = selected

    return entities


def _entry_features(config_entry: config_entries.ConfigEntry) -> dict[str, bool]:
    """Return current feature options for an existing config entry."""
    return config_entry.options.get(
        CONF_FEATURES,
        config_entry.data.get(CONF_FEATURES, DEFAULT_FEATURES),
    )


def _entry_entities(config_entry: config_entries.ConfigEntry) -> dict[str, list[str]]:
    """Return current entity options for an existing config entry."""
    stored_entities = config_entry.options.get(
        CONF_ENTITIES,
        config_entry.data.get(CONF_ENTITIES, {}),
    )
    return _normalize_stored_entities(stored_entities)


def _normalize_entity_list(value: Any) -> list[str]:
    """Normalize selector output to a sorted unique list of entity IDs."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        values = [value]
    else:
        values = list(value)

    return sorted({str(entity_id) for entity_id in values if entity_id})


def _normalize_stored_entities(stored_entities: Any) -> dict[str, list[str]]:
    """Normalize old and new entity storage formats."""
    normalized: dict[str, list[str]] = {}

    if not isinstance(stored_entities, dict):
        return normalized

    for feature, value in stored_entities.items():
        if feature not in FEATURE_KEYS:
            continue

        if isinstance(value, dict):
            entity_ids = _normalize_entity_list(value.values())
        else:
            entity_ids = _normalize_entity_list(value)

        if entity_ids:
            normalized[feature] = entity_ids

    return normalized


def _auto_detect_entities(hass: Any, enabled_features: dict[str, bool]) -> dict[str, list[str]]:
    """Suggest high-confidence entities for selected modules."""
    registry = er.async_get(hass)
    suggestions: dict[str, list[tuple[int, str]]] = {
        feature: [] for feature in FEATURE_KEYS if enabled_features.get(feature, False)
    }

    for entity_entry in registry.entities.values():
        entity_id = entity_entry.entity_id
        if entity_entry.disabled_by or entity_entry.hidden_by:
            continue
        if not entity_id.startswith(("sensor.", "binary_sensor.", "switch.")):
            continue

        state = hass.states.get(entity_id)
        haystack = _entity_haystack(entity_entry, state)

        for feature in suggestions:
            score = _auto_detect_score(feature, haystack, state)
            if score >= _AUTO_DETECT_MIN_SCORE[feature]:
                suggestions[feature].append((score, entity_id))

    return {
        feature: [entity_id for _score, entity_id in sorted(matches, reverse=True)[:10]]
        for feature, matches in suggestions.items()
        if matches
    }


def _entity_haystack(entity_entry: er.RegistryEntry, state: Any) -> str:
    """Return searchable text for an entity."""
    parts: list[str] = [entity_entry.entity_id]
    if entity_entry.name:
        parts.append(entity_entry.name)
    if entity_entry.original_name:
        parts.append(entity_entry.original_name)
    if state is not None:
        friendly_name = state.attributes.get("friendly_name")
        device_class = state.attributes.get("device_class")
        state_class = state.attributes.get("state_class")
        unit = state.attributes.get("unit_of_measurement")
        parts.extend(str(part) for part in (friendly_name, device_class, state_class, unit) if part)

    return " ".join(parts).lower()


def _auto_detect_score(feature: str, haystack: str, state: Any) -> int:
    """Score how likely an entity belongs to a feature."""
    if feature == FEATURE_BATTERY and not _is_storage_battery_candidate(haystack):
        return 0

    score = sum(2 for keyword in _AUTO_DETECT_KEYWORDS[feature] if keyword in haystack)

    if state is None:
        return score

    device_class = state.attributes.get("device_class")
    unit = state.attributes.get("unit_of_measurement")

    if feature != FEATURE_BATTERY and device_class in {"power", "energy", "battery", "monetary"}:
        score += 1
    if unit in _POWER_UNITS or unit in _ENERGY_UNITS:
        score += 1
    if feature == FEATURE_BATTERY:
        score += 3
    if feature == FEATURE_DYNAMIC_TARIFF and device_class == "monetary":
        score += 4
    if feature == FEATURE_CONTROLLABLE_LOADS and haystack.startswith("switch."):
        score += 2

    return score


def _is_storage_battery_candidate(haystack: str) -> bool:
    """Return whether a battery entity looks like a home battery system."""
    has_storage_signal = any(keyword in haystack for keyword in _BATTERY_STORAGE_KEYWORDS)
    has_small_battery_signal = any(keyword in haystack for keyword in _SMALL_BATTERY_KEYWORDS)

    if has_storage_signal:
        return True
    if has_small_battery_signal:
        return False

    return False


def _merge_entity_defaults(
    current_entities: dict[str, list[str]],
    auto_detected_entities: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Use configured entities first and auto-detected entities as fallback."""
    return {
        feature: current_entities.get(feature, auto_detected_entities.get(feature, []))
        for feature in FEATURE_KEYS
    }


class WattBalansEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the WattBalans Energy Management config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._features: dict[str, bool] = {}

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow for an existing installation."""
        return WattBalansEnergyOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle initial component selection."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            self._features = _features_from_input(user_input)
            return await self.async_step_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=_feature_schema(DEFAULT_FEATURES),
        )

    async def async_step_entities(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle optional entity selection."""
        auto_detected = _auto_detect_entities(self.hass, self._features)
        if user_input is not None:
            return self.async_create_entry(
                title="WattBalans Energy Management",
                data={
                    CONF_FEATURES: self._features,
                    CONF_ENTITIES: _entities_from_input(self._features, user_input),
                },
            )

        return self.async_show_form(
            step_id="entities",
            data_schema=_entity_schema(self._features, {}, auto_detected),
            description_placeholders={
                "auto_detected_count": str(sum(len(value) for value in auto_detected.values()))
            },
        )


class WattBalansEnergyOptionsFlow(config_entries.OptionsFlow):
    """Allow installed components and entities to be changed later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry
        self._features: dict[str, bool] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage WattBalans component options."""
        if user_input is not None:
            self._features = _features_from_input(user_input)
            return await self.async_step_entities()

        return self.async_show_form(
            step_id="init",
            data_schema=_feature_schema(_entry_features(self._config_entry)),
        )

    async def async_step_entities(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage WattBalans entity options."""
        current_entities = _entry_entities(self._config_entry)
        auto_detected = _auto_detect_entities(self.hass, self._features)
        defaults = _merge_entity_defaults(current_entities, auto_detected)

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_FEATURES: self._features,
                    CONF_ENTITIES: _entities_from_input(self._features, user_input),
                },
            )

        return self.async_show_form(
            step_id="entities",
            data_schema=_entity_schema(
                self._features,
                defaults,
                auto_detected,
            ),
            description_placeholders={
                "auto_detected_count": str(sum(len(value) for value in auto_detected.values()))
            },
        )
