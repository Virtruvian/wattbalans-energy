"""Config flow for WattBalans Energy Management."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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

ENTITY_FIELDS: dict[str, tuple[str, ...]] = {
    FEATURE_SOLAR: (
        "solar_power_entity",
        "solar_energy_today_entity",
        "solar_energy_total_entity",
    ),
    FEATURE_GRID: (
        "grid_power_entity",
        "grid_import_energy_entity",
        "grid_export_energy_entity",
    ),
    FEATURE_BATTERY: (
        "battery_soc_entity",
        "battery_power_entity",
        "battery_energy_entity",
    ),
    FEATURE_EV_CHARGING: (
        "ev_charging_power_entity",
        "ev_charging_energy_entity",
        "ev_charging_status_entity",
    ),
    FEATURE_DYNAMIC_TARIFF: (
        "dynamic_tariff_price_entity",
        "dynamic_tariff_next_price_entity",
    ),
    FEATURE_CONTROLLABLE_LOADS: (
        "controllable_load_power_entity",
        "controllable_load_switch_entity",
    ),
}


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
    current_entities: dict[str, dict[str, str]],
) -> vol.Schema:
    """Build the entity selection schema for selected features."""
    schema: dict[vol.Optional, selector.EntitySelector] = {}

    for feature in FEATURE_KEYS:
        if not enabled_features.get(feature, False):
            continue

        for field in ENTITY_FIELDS[feature]:
            schema[
                vol.Optional(field, default=current_entities.get(feature, {}).get(field, ""))
            ] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "binary_sensor", "switch"])
            )

    return vol.Schema(schema)


def _features_from_input(user_input: dict[str, Any]) -> dict[str, bool]:
    """Normalize selected features from form input."""
    return {feature: bool(user_input[feature]) for feature in FEATURE_KEYS}


def _entities_from_input(
    enabled_features: dict[str, bool],
    user_input: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Normalize selected Home Assistant entities from form input."""
    entities: dict[str, dict[str, str]] = {}

    for feature in FEATURE_KEYS:
        if not enabled_features.get(feature, False):
            continue

        selected_entities = {
            field: str(user_input[field])
            for field in ENTITY_FIELDS[feature]
            if user_input.get(field)
        }
        if selected_entities:
            entities[feature] = selected_entities

    return entities


def _entry_features(config_entry: config_entries.ConfigEntry) -> dict[str, bool]:
    """Return current feature options for an existing config entry."""
    return config_entry.options.get(
        CONF_FEATURES,
        config_entry.data.get(CONF_FEATURES, DEFAULT_FEATURES),
    )


def _entry_entities(config_entry: config_entries.ConfigEntry) -> dict[str, dict[str, str]]:
    """Return current entity options for an existing config entry."""
    return config_entry.options.get(
        CONF_ENTITIES,
        config_entry.data.get(CONF_ENTITIES, {}),
    )


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
            data_schema=_entity_schema(self._features, {}),
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
                _entry_entities(self._config_entry),
            ),
        )
