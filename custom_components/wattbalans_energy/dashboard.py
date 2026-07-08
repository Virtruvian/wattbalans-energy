"""Generate the WattBalans Lovelace dashboard configuration."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .const import (
    FEATURE_BATTERY,
    FEATURE_CONTROLLABLE_LOADS,
    FEATURE_DYNAMIC_TARIFF,
    FEATURE_EV_CHARGING,
    FEATURE_GRID,
    FEATURE_SOLAR,
)

DashboardConfig = dict[str, Any]
EntityMap = Mapping[str, tuple[str, ...]]

_FEATURE_ORDER = (
    FEATURE_SOLAR,
    FEATURE_GRID,
    FEATURE_BATTERY,
    FEATURE_EV_CHARGING,
    FEATURE_DYNAMIC_TARIFF,
    FEATURE_CONTROLLABLE_LOADS,
)

_FEATURE_LABELS = {
    FEATURE_SOLAR: "Zonnepanelen",
    FEATURE_GRID: "Netaansluiting",
    FEATURE_BATTERY: "Thuisbatterij",
    FEATURE_EV_CHARGING: "EV-laden",
    FEATURE_DYNAMIC_TARIFF: "Dynamische tarieven",
    FEATURE_CONTROLLABLE_LOADS: "Schakelbare verbruikers",
}

_FEATURE_ICONS = {
    FEATURE_SOLAR: "mdi:solar-power",
    FEATURE_GRID: "mdi:transmission-tower",
    FEATURE_BATTERY: "mdi:home-battery",
    FEATURE_EV_CHARGING: "mdi:ev-station",
    FEATURE_DYNAMIC_TARIFF: "mdi:currency-eur",
    FEATURE_CONTROLLABLE_LOADS: "mdi:power-plug",
}


def build_dashboard_config(
    enabled_features: Iterable[str],
    entity_ids: EntityMap | None = None,
) -> DashboardConfig:
    """Build a deterministic dashboard for the selected WattBalans modules."""
    enabled = set(enabled_features)
    selected = tuple(feature for feature in _FEATURE_ORDER if feature in enabled)
    entities = entity_ids or {}

    return {
        "title": "WattBalans Energy",
        "views": [
            _build_overview_view(selected),
            *(
                _build_feature_view(feature, entities.get(feature, ()))
                for feature in selected
            ),
        ],
    }


def _build_overview_view(enabled_features: tuple[str, ...]) -> DashboardConfig:
    """Build the fixed overview view."""
    if enabled_features:
        module_lines = "\n".join(
            f"- {_FEATURE_LABELS[feature]}" for feature in enabled_features
        )
    else:
        module_lines = "- Er zijn nog geen modules geselecteerd."

    return {
        "title": "Overzicht",
        "path": "overview",
        "icon": "mdi:home-lightning-bolt",
        "cards": [
            {
                "type": "markdown",
                "title": "WattBalans Energy",
                "content": (
                    "## Actieve onderdelen\n\n"
                    f"{module_lines}\n\n"
                    "De meet- en regelkaarten worden automatisch toegevoegd zodra "
                    "de bijbehorende entiteiten zijn geconfigureerd."
                ),
            }
        ],
    }


def _build_feature_view(feature: str, entity_ids: tuple[str, ...]) -> DashboardConfig:
    """Build one module view and include known entities when available."""
    cards: list[DashboardConfig] = []

    if entity_ids:
        cards.append(
            {
                "type": "entities",
                "title": _FEATURE_LABELS[feature],
                "show_header_toggle": False,
                "entities": list(entity_ids),
            }
        )
    else:
        cards.append(
            {
                "type": "markdown",
                "title": _FEATURE_LABELS[feature],
                "content": (
                    "Deze module is ingeschakeld. Koppel de bijbehorende Home "
                    "Assistant-entiteiten om hier metingen en bediening te tonen."
                ),
            }
        )

    return {
        "title": _FEATURE_LABELS[feature],
        "path": feature.replace("_", "-"),
        "icon": _FEATURE_ICONS[feature],
        "cards": cards,
    }
