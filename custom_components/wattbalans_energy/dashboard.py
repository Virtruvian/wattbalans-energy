"""Generate the WattBalans Lovelace dashboard configuration."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypedDict

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


class EntityMetadata(TypedDict, total=False):
    """Metadata used to build richer Lovelace cards."""

    device_class: str | None
    domain: str
    friendly_name: str | None
    state_class: str | None
    unit: str | None


EntityMetadataMap = Mapping[str, EntityMetadata]

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
    entity_metadata: EntityMetadataMap | None = None,
) -> DashboardConfig:
    """Build a deterministic dashboard for the selected WattBalans modules."""
    enabled = set(enabled_features)
    selected = tuple(feature for feature in _FEATURE_ORDER if feature in enabled)
    entities = entity_ids or {}
    metadata = entity_metadata or {}

    return {
        "title": "WattBalans Energy",
        "views": [
            _build_overview_view(selected, entities, metadata),
            *(
                _build_feature_view(feature, entities.get(feature, ()), metadata)
                for feature in selected
            ),
        ],
    }


def _build_overview_view(
    enabled_features: tuple[str, ...],
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Build the fixed overview view."""
    if enabled_features:
        module_lines = "\n".join(
            f"- {_FEATURE_LABELS[feature]} ({len(entity_ids.get(feature, ()))} entiteiten)"
            for feature in enabled_features
        )
    else:
        module_lines = "- Er zijn nog geen modules geselecteerd."

    cards: list[DashboardConfig] = [
        {
            "type": "markdown",
            "title": "WattBalans Energy",
            "content": (
                "## Actieve onderdelen\n\n"
                f"{module_lines}\n\n"
                "De kaarten worden automatisch opgebouwd uit de gekoppelde "
                "Home Assistant-entiteiten."
            ),
        }
    ]

    power_entities = _overview_entities(entity_ids, entity_metadata, "power")
    soc_entities = _overview_entities(entity_ids, entity_metadata, "soc")
    price_entities = _overview_entities(entity_ids, entity_metadata, "price")

    if power_entities:
        cards.append(_history_graph_card("Actueel vermogen", power_entities, hours_to_show=12))
    if soc_entities:
        cards.append(_gauge_grid_card("Accu laadniveau", soc_entities))
    if price_entities:
        cards.append(_entities_card("Dynamische tarieven", price_entities))

    return {
        "title": "Overzicht",
        "path": "overview",
        "icon": "mdi:home-lightning-bolt",
        "cards": cards,
    }


def _build_feature_view(
    feature: str,
    entity_ids: tuple[str, ...],
    entity_metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Build one module view and include known entities when available."""
    cards = _feature_cards(feature, entity_ids, entity_metadata)

    if not cards:
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


def _feature_cards(
    feature: str,
    entity_ids: tuple[str, ...],
    entity_metadata: EntityMetadataMap,
) -> list[DashboardConfig]:
    """Build cards for one feature based on entity metadata."""
    groups = _group_entities(entity_ids, entity_metadata)
    cards: list[DashboardConfig] = []

    if groups["soc"]:
        cards.append(_gauge_grid_card("Laadniveau", groups["soc"]))
    if groups["power"]:
        cards.append(_history_graph_card("Vermogen", groups["power"], hours_to_show=24))
    if groups["price"]:
        cards.append(_entities_card("Tarieven", groups["price"]))
    if groups["energy"]:
        cards.append(_entities_card("Energie", groups["energy"]))
    if groups["control"]:
        cards.append(_entities_card("Status en bediening", groups["control"]))
    if groups["other"]:
        cards.append(_entities_card(_FEATURE_LABELS[feature], groups["other"]))

    return cards


def _group_entities(
    entity_ids: tuple[str, ...],
    entity_metadata: EntityMetadataMap,
) -> dict[str, list[str]]:
    """Group entities into dashboard card categories."""
    groups: dict[str, list[str]] = {
        "soc": [],
        "power": [],
        "price": [],
        "energy": [],
        "control": [],
        "other": [],
    }

    for entity_id in entity_ids:
        groups[_entity_group(entity_id, entity_metadata.get(entity_id, {}))].append(entity_id)

    return groups


def _entity_group(entity_id: str, metadata: EntityMetadata) -> str:
    """Return the best dashboard group for an entity."""
    device_class = metadata.get("device_class")
    unit = str(metadata.get("unit") or "").lower()
    domain = metadata.get("domain") or entity_id.split(".", 1)[0]
    haystack = " ".join(
        str(value)
        for value in (
            entity_id,
            metadata.get("friendly_name"),
            device_class,
            unit,
        )
        if value
    ).lower()

    if "soc" in haystack or unit == "%" or device_class == "battery":
        return "soc"
    if device_class == "monetary" or "tarief" in haystack or "price" in haystack:
        return "price"
    if device_class == "power" or unit in {"w", "kw"}:
        return "power"
    if device_class == "energy" or unit in {"wh", "kwh"}:
        return "energy"
    if domain in {"switch", "binary_sensor"}:
        return "control"
    return "other"


def _overview_entities(
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
    group: str,
) -> list[str]:
    """Return a compact cross-module entity list for the overview."""
    selected: list[str] = []
    for feature in _FEATURE_ORDER:
        for entity_id in entity_ids.get(feature, ()):
            if _entity_group(entity_id, entity_metadata.get(entity_id, {})) == group:
                selected.append(entity_id)
    return selected[:8]


def _history_graph_card(
    title: str,
    entity_ids: list[str],
    *,
    hours_to_show: int,
) -> DashboardConfig:
    """Return a history graph card."""
    return {
        "type": "history-graph",
        "title": title,
        "hours_to_show": hours_to_show,
        "entities": entity_ids,
    }


def _gauge_grid_card(title: str, entity_ids: list[str]) -> DashboardConfig:
    """Return a grid of gauge cards."""
    return {
        "type": "grid",
        "title": title,
        "columns": 2,
        "square": False,
        "cards": [
            {
                "type": "gauge",
                "entity": entity_id,
                "min": 0,
                "max": 100,
                "severity": {
                    "green": 50,
                    "yellow": 20,
                    "red": 0,
                },
            }
            for entity_id in entity_ids[:6]
        ],
    }


def _entities_card(title: str, entity_ids: list[str]) -> DashboardConfig:
    """Return an entities card."""
    return {
        "type": "entities",
        "title": title,
        "show_header_toggle": False,
        "entities": entity_ids,
    }
