"""Config flow for WattBalans Energy Management."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
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


def _features_from_input(user_input: dict[str, Any]) -> dict[str, bool]:
    """Normalize selected features from form input."""
    return {feature: bool(user_input[feature]) for feature in FEATURE_KEYS}


class WattBalansEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the WattBalans Energy Management config flow."""

    VERSION = 1

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
            return self.async_create_entry(
                title="WattBalans Energy Management",
                data={CONF_FEATURES: _features_from_input(user_input)},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_feature_schema(DEFAULT_FEATURES),
        )


class WattBalansEnergyOptionsFlow(config_entries.OptionsFlow):
    """Allow installed components to be changed later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage WattBalans component options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={CONF_FEATURES: _features_from_input(user_input)},
            )

        current_features = self._config_entry.options.get(
            CONF_FEATURES,
            self._config_entry.data.get(CONF_FEATURES, DEFAULT_FEATURES),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=_feature_schema(current_features),
        )
