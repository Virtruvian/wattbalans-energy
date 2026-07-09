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
    """Build a calm SEM-inspired home overview."""
    cards: list[DashboardConfig] = [_overview_header_card(enabled_features, entity_ids)]

    kpis = _kpi_cards(entity_ids, entity_metadata)
    if kpis:
        cards.append({"type": "grid", "title": "Nu", "columns": 3, "square": False, "cards": kpis})

    sections = _overview_section_cards(entity_ids, entity_metadata)
    if sections:
        cards.append({"type": "grid", "title": "Energieoverzicht", "columns": 2, "square": False, "cards": sections})

    trend_entities = _overview_trend_entities(entity_ids, entity_metadata)
    if trend_entities:
        cards.append(_statistics_graph_card("Trend laatste 24 uur", trend_entities, days_to_show=1))

    return {"title": "Overzicht", "path": "overview", "icon": "mdi:view-dashboard", "cards": cards}


def _overview_header_card(enabled_features: tuple[str, ...], entity_ids: EntityMap) -> DashboardConfig:
    """Return the compact dashboard header."""
    if enabled_features:
        modules = "  ".join(
            f"**{_FEATURE_ACCENT[feature]} {_FEATURE_LABELS[feature]}** · {len(entity_ids.get(feature, ()))}"
            for feature in enabled_features
        )
    else:
        modules = "Er zijn nog geen modules geselecteerd."

    return {
        "type": "markdown",
        "content": "# WattBalans Energy\n\nCompact overzicht van opwek, net, opslag, laden en verbruik.\n\n" + modules,
    }


def _kpi_cards(entity_ids: EntityMap, entity_metadata: EntityMetadataMap) -> list[DashboardConfig]:
    """Return the most important KPI tiles for the overview."""
    candidates = (
        (FEATURE_SOLAR, "Zon nu", _first_group(entity_ids, entity_metadata, FEATURE_SOLAR, "power")),
        (FEATURE_GRID, "Net nu", _first_group(entity_ids, entity_metadata, FEATURE_GRID, "power")),
        (FEATURE_BATTERY, "Accu SOC", _first_group(entity_ids, entity_metadata, FEATURE_BATTERY, "soc")),
        (FEATURE_BATTERY, "Accu nu", _first_group(entity_ids, entity_metadata, FEATURE_BATTERY, "power")),
        (FEATURE_EV_CHARGING, "EV laden", _first_group(entity_ids, entity_metadata, FEATURE_EV_CHARGING, "power")),
        (FEATURE_DYNAMIC_TARIFF, "Tarief", _first_group(entity_ids, entity_metadata, FEATURE_DYNAMIC_TARIFF, "price")),
        (FEATURE_CONTROLLABLE_LOADS, "Verbruikers", _first_group(entity_ids, entity_metadata, FEATURE_CONTROLLABLE_LOADS, "power")),
    )
    return [_tile_card(entity_id, name, _FEATURE_ICONS[feature]) for feature, name, entity_id in candidates if entity_id][:8]


def _overview_section_cards(entity_ids: EntityMap, entity_metadata: EntityMetadataMap) -> list[DashboardConfig]:
    """Return clean overview summary cards."""
    sections = (
        ("Productie & net", (FEATURE_SOLAR, FEATURE_GRID)),
        ("Opslag & laden", (FEATURE_BATTERY, FEATURE_EV_CHARGING)),
        ("Verbruik & prijs", (FEATURE_CONTROLLABLE_LOADS, FEATURE_DYNAMIC_TARIFF)),
    )
    cards: list[DashboardConfig] = []
    for title, features in sections:
        entities = _combined_priority_entities(features, entity_ids, entity_metadata, limit=6)
        if entities:
            cards.append(_entities_card(title, entities, entity_metadata))
    return cards


def _build_feature_view(feature: str, entity_ids: tuple[str, ...], entity_metadata: EntityMetadataMap) -> DashboardConfig:
    """Build one module view."""
    cards: list[DashboardConfig] = [
        {"type": "markdown", "content": f"# {_FEATURE_ACCENT[feature]} {_FEATURE_LABELS[feature]}"}
    ]
    cards.extend(_feature_cards(feature, entity_ids, entity_metadata))

    if len(cards) == 1:
        cards.append({"type": "markdown", "title": _FEATURE_LABELS[feature], "content": "Koppel entiteiten via Opties om hier metingen te tonen."})

    return {"title": _FEATURE_LABELS[feature], "path": feature.replace("_", "-"), "icon": _FEATURE_ICONS[feature], "cards": cards}


def _feature_cards(feature: str, entity_ids: tuple[str, ...], entity_metadata: EntityMetadataMap) -> list[DashboardConfig]:
    """Build cards for a module."""
    groups = _group_entities(entity_ids, entity_metadata)
    cards: list[DashboardConfig] = []
    primary = _priority_entities(feature, entity_ids, entity_metadata)

    if primary:
        cards.append(
            {
                "type": "grid",
                "title": "Belangrijkste waarden",
                "columns": 3,
                "square": False,
                "cards": [_tile_card(entity_id, _short_entity_name(entity_id, entity_metadata), _FEATURE_ICONS[feature]) for entity_id in primary[:6]],
            }
        )
    if groups["soc"]:
        cards.append(_gauge_grid_card("Laadniveau", groups["soc"], entity_metadata))
    if groups["power"]:
        cards.append(_statistics_graph_card("Vermogenstrend", groups["power"], days_to_show=1))
    if groups["energy"]:
        cards.append(_entities_card("Energie", groups["energy"], entity_metadata))
    if groups["price"]:
        cards.append(_entities_card("Tarieven", groups["price"], entity_metadata))
    if groups["control"]:
        cards.append(_entities_card("Status en bediening", groups["control"], entity_metadata))
    if groups["other"]:
        cards.append(_entities_card("Overige waarden", groups["other"], entity_metadata))
    return cards


def _group_entities(entity_ids: tuple[str, ...], entity_metadata: EntityMetadataMap) -> dict[str, list[str]]:
    """Group entities into dashboard categories."""
    groups = {"soc": [], "power": [], "price": [], "energy": [], "control": [], "other": []}
    for entity_id in entity_ids:
        groups[_entity_group(entity_id, entity_metadata.get(entity_id, {}))].append(entity_id)
    return groups


def _entity_group(entity_id: str, metadata: EntityMetadata) -> str:
    """Return the best group for an entity."""
    device_class = metadata.get("device_class")
    unit = str(metadata.get("unit") or "").lower()
    domain = metadata.get("domain") or entity_id.split(".", 1)[0]
    text = _entity_text(entity_id, metadata)

    if "soc" in text or unit == "%" or device_class == "battery":
        return "soc"
    if device_class == "monetary" or any(word in text for word in ("tarief", "price", "cost", "kosten")):
        return "price"
    if device_class == "power" or unit in {"w", "kw"}:
        return "power"
    if device_class == "energy" or unit in {"wh", "kwh"}:
        return "energy"
    if domain in {"switch", "binary_sensor"}:
        return "control"
    return "other"


def _first_group(entity_ids: EntityMap, entity_metadata: EntityMetadataMap, feature: str, group: str) -> str | None:
    """Return the first priority entity for a feature/group."""
    for entity_id in _priority_entities(feature, entity_ids.get(feature, ()), entity_metadata):
        if _entity_group(entity_id, entity_metadata.get(entity_id, {})) == group:
            return entity_id
    return None


def _priority_entities(feature: str, entity_ids: tuple[str, ...], entity_metadata: EntityMetadataMap) -> list[str]:
    """Return useful entities in a good visual order."""
    priority_order = {
        FEATURE_SOLAR: ("power", "energy", "other", "control", "soc", "price"),
        FEATURE_GRID: ("power", "energy", "other", "price", "control", "soc"),
        FEATURE_BATTERY: ("soc", "power", "energy", "other", "control", "price"),
        FEATURE_EV_CHARGING: ("power", "energy", "control", "other", "soc", "price"),
        FEATURE_DYNAMIC_TARIFF: ("price", "other", "energy", "power", "control", "soc"),
        FEATURE_CONTROLLABLE_LOADS: ("power", "energy", "control", "other", "soc", "price"),
    }
    groups = _group_entities(entity_ids, entity_metadata)
    result: list[str] = []
    for group in priority_order[feature]:
        for entity_id in groups[group]:
            if entity_id not in result:
                result.append(entity_id)
    return result


def _combined_priority_entities(features: tuple[str, ...], entity_ids: EntityMap, entity_metadata: EntityMetadataMap, *, limit: int) -> list[str]:
    """Return compact entities across features."""
    result: list[str] = []
    for feature in features:
        for entity_id in _priority_entities(feature, entity_ids.get(feature, ()), entity_metadata):
            if entity_id not in result:
                result.append(entity_id)
    return result[:limit]


def _overview_trend_entities(entity_ids: EntityMap, entity_metadata: EntityMetadataMap) -> list[str]:
    """Return a few entities for the overview trend graph."""
    result: list[str] = []
    for feature in (FEATURE_SOLAR, FEATURE_GRID, FEATURE_BATTERY, FEATURE_CONTROLLABLE_LOADS):
        entity_id = _first_group(entity_ids, entity_metadata, feature, "power")
        if entity_id:
            result.append(entity_id)
    return result[:6]


def _entity_text(entity_id: str, metadata: EntityMetadata) -> str:
    """Return searchable text for an entity."""
    return " ".join(str(value) for value in (entity_id, metadata.get("friendly_name"), metadata.get("device_class"), metadata.get("unit")) if value).lower()


def _source_name(entity_id: str, metadata: EntityMetadata) -> str | None:
    """Infer a compact source name."""
    text = _entity_text(entity_id, metadata)
    for needle, label in (
        ("solaredge", "SolarEdge"),
        ("solarman-pv1", "PV1"),
        ("solarman-pv2", "PV2"),
        ("solarman-pv3", "PV3"),
        ("solarman-pv4", "PV4"),
        ("solarman", "Solarman"),
        ("alpha ess", "Alpha ESS"),
        ("zinvolt", "ZinVolt"),
        ("p1 meter", "P1"),
        ("p1_", "P1"),
        ("p1 ", "P1"),
        ("passat", "Passat"),
        ("wasmachine", "Wasmachine"),
        ("droger", "Droger"),
        ("koelkast", "Koelkast"),
        ("vriezer", "Vriezer"),
        ("lava", "Lava"),
    ):
        if needle in text:
            return label
    return None


def _role_name(entity_id: str, metadata: EntityMetadata) -> str:
    """Infer a compact role name."""
    text = _entity_text(entity_id, metadata)
    group = _entity_group(entity_id, metadata)
    if group == "soc":
        return "SOC"
    if group == "price":
        return "Kosten" if "cost" in text else "Prijs"
    if group == "power":
        if any(word in text for word in ("charge", "laden", "laad")):
            return "laden"
        if any(word in text for word in ("discharge", "ontladen", "ontlaad")):
            return "ontladen"
        if any(word in text for word in ("import", "afname")):
            return "afname"
        if any(word in text for word in ("export", "teruglever")):
            return "teruglevering"
        return "vermogen"
    if group == "energy":
        if any(word in text for word in ("today", "vandaag")):
            return "vandaag"
        if any(word in text for word in ("charge", "laden", "laad")):
            return "laden"
        if any(word in text for word in ("discharge", "ontladen", "ontlaad")):
            return "ontladen"
        if any(word in text for word in ("import", "afname")):
            return "import"
        if any(word in text for word in ("export", "teruglever")):
            return "export"
        return "energie"
    if group == "control":
        return "status"
    return str(metadata.get("friendly_name") or entity_id)


def _short_entity_name(entity_id: str, entity_metadata: EntityMetadataMap) -> str:
    """Return a short display name."""
    metadata = entity_metadata.get(entity_id, {})
    source = _source_name(entity_id, metadata)
    role = _role_name(entity_id, metadata)
    if source:
        return f"{source} {role}" if role not in source.lower() else source
    return role.capitalize() if len(role) < 20 else role


def _entity_entry(entity_id: str, name: str) -> dict[str, str]:
    """Return a named entity entry."""
    return {"entity": entity_id, "name": name}


def _tile_card(entity_id: str, name: str, icon: str) -> DashboardConfig:
    """Return a compact tile card."""
    return {"type": "tile", "entity": entity_id, "name": name, "icon": icon, "vertical": False, "hide_state": False}


def _statistics_graph_card(title: str, entity_ids: list[str], *, days_to_show: int) -> DashboardConfig:
    """Return a smoother statistics graph."""
    return {
        "type": "statistics-graph",
        "title": title,
        "chart_type": "line",
        "days_to_show": days_to_show,
        "period": "5minute",
        "stat_types": ["mean"],
        "entities": entity_ids,
    }


def _gauge_grid_card(title: str, entity_ids: list[str], entity_metadata: EntityMetadataMap) -> DashboardConfig:
    """Return a grid of gauge cards."""
    return {
        "type": "grid",
        "title": title,
        "columns": 2,
        "square": False,
        "cards": [
            {"type": "gauge", "entity": entity_id, "name": _short_entity_name(entity_id, entity_metadata), "min": 0, "max": 100, "severity": {"green": 50, "yellow": 20, "red": 0}}
            for entity_id in entity_ids[:6]
        ],
    }


def _entities_card(title: str, entity_ids: list[str], entity_metadata: EntityMetadataMap) -> DashboardConfig:
    """Return an entities card with compact names."""
    return {"type": "entities", "title": title, "show_header_toggle": False, "state_color": True, "entities": [_entity_entry(entity_id, _short_entity_name(entity_id, entity_metadata)) for entity_id in entity_ids]}
