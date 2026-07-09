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

_FEATURE_ACCENT = {
    FEATURE_SOLAR: "☀️",
    FEATURE_GRID: "⚡",
    FEATURE_BATTERY: "🔋",
    FEATURE_EV_CHARGING: "🚗",
    FEATURE_DYNAMIC_TARIFF: "€",
    FEATURE_CONTROLLABLE_LOADS: "🔌",
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
            _build_sem_overview_view(selected, entities, metadata),
            *(
                _build_feature_view(feature, entities.get(feature, ()), metadata)
                for feature in selected
            ),
        ],
    }


def _build_sem_overview_view(
    enabled_features: tuple[str, ...],
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Build a SEM-inspired overview with KPI tiles, flow and compact modules."""
    cards: list[DashboardConfig] = [
        _overview_header_card(enabled_features, entity_ids),
    ]

    kpi_cards = _kpi_cards(entity_ids, entity_metadata)
    if kpi_cards:
        cards.append(
            {
                "type": "grid",
                "title": "Actuele energiestatus",
                "columns": 3,
                "square": False,
                "cards": kpi_cards,
            }
        )

    cards.append(_energy_flow_card(entity_ids, entity_metadata))

    module_cards = _module_summary_cards(enabled_features, entity_ids, entity_metadata)
    if module_cards:
        cards.append(
            {
                "type": "grid",
                "title": "Onderdelen",
                "columns": 2,
                "square": False,
                "cards": module_cards,
            }
        )

    power_entities = _overview_entities(entity_ids, entity_metadata, "power")
    if power_entities:
        cards.append(_history_graph_card("Vermogen laatste 12 uur", power_entities, hours_to_show=12))

    return {
        "title": "Overzicht",
        "path": "overview",
        "icon": "mdi:view-dashboard",
        "cards": cards,
    }


def _overview_header_card(
    enabled_features: tuple[str, ...],
    entity_ids: EntityMap,
) -> DashboardConfig:
    """Return the compact dashboard header."""
    if enabled_features:
        module_lines = "  ".join(
            f"**{_FEATURE_ACCENT[feature]} {_FEATURE_LABELS[feature]}** · "
            f"{len(entity_ids.get(feature, ()))} entiteiten"
            for feature in enabled_features
        )
    else:
        module_lines = "Er zijn nog geen modules geselecteerd."

    return {
        "type": "markdown",
        "content": (
            "# WattBalans Energy\n\n"
            "SEM-inspired overzicht voor actuele energiestromen, opslag, net en "
            "slimme verbruikers.\n\n"
            f"{module_lines}"
        ),
    }


def _kpi_cards(
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
) -> list[DashboardConfig]:
    """Return the most important KPI tiles for the overview."""
    candidates = (
        ("Zon nu", "mdi:solar-power", _first_role(entity_ids, entity_metadata, FEATURE_SOLAR, "power")),
        ("Net nu", "mdi:transmission-tower", _first_role(entity_ids, entity_metadata, FEATURE_GRID, "power")),
        ("Accu SOC", "mdi:battery-heart", _first_role(entity_ids, entity_metadata, FEATURE_BATTERY, "soc")),
        ("Accu nu", "mdi:home-battery", _first_role(entity_ids, entity_metadata, FEATURE_BATTERY, "power")),
        ("EV laden", "mdi:ev-station", _first_role(entity_ids, entity_metadata, FEATURE_EV_CHARGING, "power")),
        ("Tarief", "mdi:currency-eur", _first_role(entity_ids, entity_metadata, FEATURE_DYNAMIC_TARIFF, "price")),
        (
            "Verbruikers",
            "mdi:power-plug",
            _first_role(entity_ids, entity_metadata, FEATURE_CONTROLLABLE_LOADS, "power"),
        ),
    )

    return [
        _tile_card(entity_id, name, icon)
        for name, icon, entity_id in candidates
        if entity_id
    ][:8]


def _energy_flow_card(
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Return a native Lovelace approximation of a SEM-like energy flow."""
    solar_power = _first_role(entity_ids, entity_metadata, FEATURE_SOLAR, "power")
    grid_power = _first_role(entity_ids, entity_metadata, FEATURE_GRID, "power")
    battery_power = _first_role(entity_ids, entity_metadata, FEATURE_BATTERY, "power")
    battery_soc = _first_role(entity_ids, entity_metadata, FEATURE_BATTERY, "soc")
    ev_power = _first_role(entity_ids, entity_metadata, FEATURE_EV_CHARGING, "power")
    load_power = _first_role(entity_ids, entity_metadata, FEATURE_CONTROLLABLE_LOADS, "power")

    return {
        "type": "vertical-stack",
        "cards": [
            {
                "type": "markdown",
                "content": "## Energiestroom\nKernbronnen en verbruikers in één overzicht.",
            },
            {
                "type": "grid",
                "columns": 5,
                "square": False,
                "cards": [
                    _flow_node("Zon", "mdi:solar-power", solar_power),
                    _arrow_card("→"),
                    _flow_node("Huis", "mdi:home-lightning-bolt"),
                    _arrow_card("↔"),
                    _flow_node("Net", "mdi:transmission-tower", grid_power),
                    _flow_node("Accu", "mdi:home-battery", battery_power or battery_soc),
                    _arrow_card("↕"),
                    _flow_node("Balans", "mdi:scale-balance"),
                    _arrow_card("→"),
                    _flow_node("EV", "mdi:ev-station", ev_power),
                    _flow_node("Verbruikers", "mdi:power-plug", load_power),
                    _arrow_card("→"),
                    _flow_node("Slim sturen", "mdi:lightning-bolt-circle"),
                    _arrow_card("↔"),
                    _flow_node("Opslag", "mdi:battery-sync", battery_soc),
                ],
            },
        ],
    }


def _flow_node(
    name: str,
    icon: str,
    entity_id: str | None = None,
) -> DashboardConfig:
    """Return one node in the native energy-flow approximation."""
    if entity_id:
        return _tile_card(entity_id, name, icon)

    return {
        "type": "markdown",
        "content": f"### <ha-icon icon=\"{icon}\"></ha-icon> {name}\nNog geen bron",
    }


def _arrow_card(arrow: str) -> DashboardConfig:
    """Return a visual arrow card for the native flow."""
    return {
        "type": "markdown",
        "content": f"# {arrow}",
    }


def _module_summary_cards(
    enabled_features: tuple[str, ...],
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
) -> list[DashboardConfig]:
    """Return compact module cards for the overview."""
    cards: list[DashboardConfig] = []

    for feature in enabled_features:
        module_entities = entity_ids.get(feature, ())
        if not module_entities:
            cards.append(
                {
                    "type": "markdown",
                    "title": _FEATURE_LABELS[feature],
                    "content": "Module actief, maar nog geen entiteiten gekoppeld.",
                }
            )
            continue

        priority_entities = _priority_entities(feature, module_entities, entity_metadata)
        cards.append(
            {
                "type": "entities",
                "title": f"{_FEATURE_ACCENT[feature]} {_FEATURE_LABELS[feature]}",
                "show_header_toggle": False,
                "entities": priority_entities[:5],
            }
        )

    return cards


def _build_feature_view(
    feature: str,
    entity_ids: tuple[str, ...],
    entity_metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Build one module view and include known entities when available."""
    cards: list[DashboardConfig] = [
        {
            "type": "markdown",
            "content": f"# {_FEATURE_ACCENT[feature]} {_FEATURE_LABELS[feature]}",
        }
    ]
    cards.extend(_feature_cards(feature, entity_ids, entity_metadata))

    if len(cards) == 1:
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

    primary_entities = _priority_entities(feature, entity_ids, entity_metadata)
    if primary_entities:
        cards.append(
            {
                "type": "grid",
                "title": "Belangrijkste waarden",
                "columns": 3,
                "square": False,
                "cards": [
                    _tile_card(entity_id, _tile_name(entity_id, entity_metadata), _FEATURE_ICONS[feature])
                    for entity_id in primary_entities[:6]
                ],
            }
        )

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
        cards.append(_entities_card("Overige waarden", groups["other"]))

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
    haystack = _entity_haystack(entity_id, metadata)

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


def _first_role(
    entity_ids: EntityMap,
    entity_metadata: EntityMetadataMap,
    feature: str,
    group: str,
) -> str | None:
    """Return the first entity for a feature/group combination."""
    for entity_id in entity_ids.get(feature, ()):
        if _entity_group(entity_id, entity_metadata.get(entity_id, {})) == group:
            return entity_id
    return None


def _priority_entities(
    feature: str,
    entity_ids: tuple[str, ...],
    entity_metadata: EntityMetadataMap,
) -> list[str]:
    """Return the most useful entities for compact module cards."""
    priority_order = {
        FEATURE_SOLAR: ("power", "energy", "other", "control", "soc", "price"),
        FEATURE_GRID: ("power", "energy", "price", "other", "control", "soc"),
        FEATURE_BATTERY: ("soc", "power", "energy", "other", "control", "price"),
        FEATURE_EV_CHARGING: ("power", "energy", "control", "other", "soc", "price"),
        FEATURE_DYNAMIC_TARIFF: ("price", "other", "energy", "power", "control", "soc"),
        FEATURE_CONTROLLABLE_LOADS: ("power", "energy", "control", "other", "soc", "price"),
    }
    grouped = _group_entities(entity_ids, entity_metadata)
    prioritized: list[str] = []
    for group in priority_order[feature]:
        prioritized.extend(grouped[group])
    return prioritized


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


def _entity_haystack(entity_id: str, metadata: EntityMetadata) -> str:
    """Return searchable text for one entity."""
    return " ".join(
        str(value)
        for value in (
            entity_id,
            metadata.get("friendly_name"),
            metadata.get("device_class"),
            metadata.get("unit"),
        )
        if value
    ).lower()


def _tile_name(entity_id: str, entity_metadata: EntityMetadataMap) -> str:
    """Return a readable tile name."""
    return str(entity_metadata.get(entity_id, {}).get("friendly_name") or entity_id)


def _tile_card(entity_id: str, name: str, icon: str) -> DashboardConfig:
    """Return a compact native tile card."""
    return {
        "type": "tile",
        "entity": entity_id,
        "name": name,
        "icon": icon,
        "vertical": False,
    }


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
