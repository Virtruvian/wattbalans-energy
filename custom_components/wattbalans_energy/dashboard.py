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
    """Metadata used to build dashboard cards."""

    device_class: str | None
    domain: str
    friendly_name: str | None
    state_class: str | None
    unit: str | None


EntityMetadataMap = Mapping[str, EntityMetadata]

FEATURE_ORDER = (
    FEATURE_SOLAR,
    FEATURE_GRID,
    FEATURE_BATTERY,
    FEATURE_EV_CHARGING,
    FEATURE_DYNAMIC_TARIFF,
    FEATURE_CONTROLLABLE_LOADS,
)

FEATURE_LABELS = {
    FEATURE_SOLAR: "Zon",
    FEATURE_GRID: "Net",
    FEATURE_BATTERY: "Batterij",
    FEATURE_EV_CHARGING: "EV",
    FEATURE_DYNAMIC_TARIFF: "Kosten",
    FEATURE_CONTROLLABLE_LOADS: "Slim",
}

FEATURE_LONG_LABELS = {
    FEATURE_SOLAR: "Zonnepanelen",
    FEATURE_GRID: "Netaansluiting",
    FEATURE_BATTERY: "Batterij",
    FEATURE_EV_CHARGING: "EV-laden",
    FEATURE_DYNAMIC_TARIFF: "Kosten & tarieven",
    FEATURE_CONTROLLABLE_LOADS: "Slimme apparaten",
}

FEATURE_ICONS = {
    FEATURE_SOLAR: "mdi:solar-power",
    FEATURE_GRID: "mdi:transmission-tower",
    FEATURE_BATTERY: "mdi:home-battery",
    FEATURE_EV_CHARGING: "mdi:ev-station",
    FEATURE_DYNAMIC_TARIFF: "mdi:currency-eur",
    FEATURE_CONTROLLABLE_LOADS: "mdi:power-plug",
}

FEATURE_EMOJI = {
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
    """Build a dashboard based on the energy-regie structure."""
    enabled = set(enabled_features)
    selected = tuple(feature for feature in FEATURE_ORDER if feature in enabled)
    entities = entity_ids or {}
    metadata = entity_metadata or {}

    return {
        "title": "WattBalans Energy",
        "views": [
            _overview_view(selected, entities, metadata),
            *(
                _module_view(feature, entities.get(feature, ()), metadata)
                for feature in selected
            ),
        ],
    }


def _overview_view(
    selected: tuple[str, ...],
    entity_ids: EntityMap,
    metadata: EntityMetadataMap,
) -> DashboardConfig:
    """Build the energy-regie overview page."""
    cards: list[DashboardConfig] = [
        {
            "type": "markdown",
            "content": (
                "# Energie regie\n\n"
                "Overzicht van opwek, verbruik, opslag, laden, net en kosten. "
                "De onderdelen hieronder worden automatisch opgebouwd uit de modules die aanwezig zijn."
            ),
        },
        _flow_card(selected, entity_ids, metadata),
    ]

    kpis = _kpi_cards(entity_ids, metadata)
    if kpis:
        cards.append({"type": "grid", "title": "Nu", "columns": 3, "square": False, "cards": kpis})

    regie_cards = _regie_summary_cards(selected, entity_ids, metadata)
    if regie_cards:
        cards.append({"type": "grid", "title": "Regieblokken", "columns": 2, "square": False, "cards": regie_cards})

    trend_entities = _overview_trend_entities(entity_ids, metadata)
    if trend_entities:
        cards.append(_trend_card("Regietrend", trend_entities))

    return {"title": "Regie", "path": "overview", "icon": "mdi:view-dashboard", "cards": cards}


def _flow_card(selected: tuple[str, ...], entity_ids: EntityMap, metadata: EntityMetadataMap) -> DashboardConfig:
    """Build a simple, readable native flowchart."""
    nodes = {
        FEATURE_SOLAR: _flow_node(FEATURE_SOLAR, _first_group(entity_ids, metadata, FEATURE_SOLAR, "power"), metadata),
        FEATURE_GRID: _flow_node(FEATURE_GRID, _first_group(entity_ids, metadata, FEATURE_GRID, "power"), metadata),
        FEATURE_BATTERY: _flow_node(FEATURE_BATTERY, _first_group(entity_ids, metadata, FEATURE_BATTERY, "soc") or _first_group(entity_ids, metadata, FEATURE_BATTERY, "power"), metadata),
        FEATURE_EV_CHARGING: _flow_node(FEATURE_EV_CHARGING, _first_group(entity_ids, metadata, FEATURE_EV_CHARGING, "power"), metadata),
        FEATURE_DYNAMIC_TARIFF: _flow_node(FEATURE_DYNAMIC_TARIFF, _first_group(entity_ids, metadata, FEATURE_DYNAMIC_TARIFF, "price"), metadata),
        FEATURE_CONTROLLABLE_LOADS: _flow_node(FEATURE_CONTROLLABLE_LOADS, _first_group(entity_ids, metadata, FEATURE_CONTROLLABLE_LOADS, "power"), metadata),
    }

    solar = nodes[FEATURE_SOLAR] if FEATURE_SOLAR in selected else "☀️ Zon\n_niet aanwezig_"
    grid = nodes[FEATURE_GRID] if FEATURE_GRID in selected else "⚡ Net\n_niet gekoppeld_"
    battery = nodes[FEATURE_BATTERY] if FEATURE_BATTERY in selected else "🔋 Batterij\n_niet aanwezig_"
    ev = nodes[FEATURE_EV_CHARGING] if FEATURE_EV_CHARGING in selected else "🚗 EV\n_niet aanwezig_"
    loads = nodes[FEATURE_CONTROLLABLE_LOADS] if FEATURE_CONTROLLABLE_LOADS in selected else "🔌 Slim\n_niet aanwezig_"
    cost = nodes[FEATURE_DYNAMIC_TARIFF] if FEATURE_DYNAMIC_TARIFF in selected else "€ Kosten\n_niet gekoppeld_"

    return {
        "type": "markdown",
        "title": "Energieflow",
        "content": (
            "```text\n"
            f"{solar}\n"
            "        │\n"
            "        ▼\n"
            "🏠 Huis / verbruik\n"
            "        │\n"
            f"        ├──▶ {loads}\n"
            f"        ├──▶ {ev}\n"
            f"        ├──↔ {battery}\n"
            f"        └──↔ {grid}\n\n"
            f"Regie op basis van: {cost}\n"
            "```"
        ),
    }


def _flow_node(feature: str, entity_id: str | None, metadata: EntityMetadataMap) -> str:
    """Return a compact text node for the flowchart."""
    label = f"{FEATURE_EMOJI[feature]} {FEATURE_LABELS[feature]}"
    return f"{label}\n{_short_name(entity_id, metadata) if entity_id else 'geen bron'}"


def _kpi_cards(entity_ids: EntityMap, metadata: EntityMetadataMap) -> list[DashboardConfig]:
    """Return compact KPI tiles."""
    candidates = (
        (FEATURE_SOLAR, "Zon", _first_group(entity_ids, metadata, FEATURE_SOLAR, "power")),
        (FEATURE_GRID, "Net", _first_group(entity_ids, metadata, FEATURE_GRID, "power")),
        (FEATURE_BATTERY, "Accu SOC", _first_group(entity_ids, metadata, FEATURE_BATTERY, "soc")),
        (FEATURE_BATTERY, "Accu", _first_group(entity_ids, metadata, FEATURE_BATTERY, "power")),
        (FEATURE_EV_CHARGING, "EV", _first_group(entity_ids, metadata, FEATURE_EV_CHARGING, "power")),
        (FEATURE_DYNAMIC_TARIFF, "Kosten", _first_group(entity_ids, metadata, FEATURE_DYNAMIC_TARIFF, "price")),
        (FEATURE_CONTROLLABLE_LOADS, "Slim", _first_group(entity_ids, metadata, FEATURE_CONTROLLABLE_LOADS, "power")),
    )
    return [_tile(entity_id, name, FEATURE_ICONS[feature]) for feature, name, entity_id in candidates if entity_id]


def _regie_summary_cards(selected: tuple[str, ...], entity_ids: EntityMap, metadata: EntityMetadataMap) -> list[DashboardConfig]:
    """Return summary cards for the overview."""
    definitions = (
        ("Opwek & net", (FEATURE_SOLAR, FEATURE_GRID)),
        ("Opslag & laden", (FEATURE_BATTERY, FEATURE_EV_CHARGING)),
        ("Slim sturen", (FEATURE_CONTROLLABLE_LOADS, FEATURE_DYNAMIC_TARIFF)),
    )
    cards: list[DashboardConfig] = []
    for title, features in definitions:
        entities = _combined_priority_entities(tuple(f for f in features if f in selected), entity_ids, metadata, limit=6)
        if entities:
            cards.append(_entities_card(title, entities, metadata))
    return cards


def _module_view(feature: str, entity_ids: tuple[str, ...], metadata: EntityMetadataMap) -> DashboardConfig:
    """Build a detail page for one energy-regie part."""
    cards: list[DashboardConfig] = [
        {"type": "markdown", "content": f"# {FEATURE_EMOJI[feature]} {FEATURE_LONG_LABELS[feature]}"}
    ]

    priority = _priority_entities(feature, entity_ids, metadata)
    if priority:
        cards.append({"type": "grid", "title": "Belangrijk", "columns": 3, "square": False, "cards": [_tile(e, _short_name(e, metadata), FEATURE_ICONS[feature]) for e in priority[:6]]})

    groups = _group_entities(entity_ids, metadata)
    if groups["soc"]:
        cards.append(_gauge_grid("Laadniveau", groups["soc"], metadata))
    if groups["power"]:
        cards.append(_trend_card("Vermogen", groups["power"][:6]))
    if groups["energy"]:
        cards.append(_entities_card("Energie", groups["energy"], metadata))
    if groups["price"]:
        cards.append(_entities_card("Kosten & tarieven", groups["price"], metadata))
    if groups["control"]:
        cards.append(_entities_card("Status & bediening", groups["control"], metadata))
    if groups["other"]:
        cards.append(_entities_card("Overig", groups["other"], metadata))

    if len(cards) == 1:
        cards.append({"type": "markdown", "content": "Geen entiteiten gekoppeld. Open Opties om bronnen te selecteren."})

    return {"title": FEATURE_LABELS[feature], "path": feature.replace("_", "-"), "icon": FEATURE_ICONS[feature], "cards": cards}


def _group_entities(entity_ids: tuple[str, ...], metadata: EntityMetadataMap) -> dict[str, list[str]]:
    """Group entities by role."""
    groups = {"soc": [], "power": [], "energy": [], "price": [], "control": [], "other": []}
    for entity_id in entity_ids:
        groups[_entity_group(entity_id, metadata.get(entity_id, {}))].append(entity_id)
    return groups


def _entity_group(entity_id: str, metadata: EntityMetadata) -> str:
    """Return the best role for one entity."""
    device_class = metadata.get("device_class")
    unit = str(metadata.get("unit") or "").lower()
    domain = metadata.get("domain") or entity_id.split(".", 1)[0]
    text = _text(entity_id, metadata)
    if _price_label(text) is not None:
        return "price"
    if "soc" in text or unit == "%" or device_class == "battery":
        return "soc"
    if device_class == "monetary" or any(w in text for w in ("tarief", "price", "prijs", "cost", "kosten")):
        return "price"
    if device_class == "power" or unit in {"w", "kw"}:
        return "power"
    if device_class == "energy" or unit in {"wh", "kwh"}:
        return "energy"
    if domain in {"switch", "binary_sensor"}:
        return "control"
    return "other"


def _first_group(entity_ids: EntityMap, metadata: EntityMetadataMap, feature: str, group: str) -> str | None:
    """Return first entity from a group."""
    for entity_id in _priority_entities(feature, entity_ids.get(feature, ()), metadata):
        if _entity_group(entity_id, metadata.get(entity_id, {})) == group:
            return entity_id
    return None


def _priority_entities(feature: str, entity_ids: tuple[str, ...], metadata: EntityMetadataMap) -> list[str]:
    """Return entities in a useful order."""
    order = {
        FEATURE_SOLAR: ("power", "energy", "other", "control", "soc", "price"),
        FEATURE_GRID: ("power", "energy", "price", "other", "control", "soc"),
        FEATURE_BATTERY: ("soc", "power", "energy", "other", "control", "price"),
        FEATURE_EV_CHARGING: ("power", "energy", "control", "other", "soc", "price"),
        FEATURE_DYNAMIC_TARIFF: ("price", "other", "energy", "power", "control", "soc"),
        FEATURE_CONTROLLABLE_LOADS: ("power", "energy", "control", "other", "soc", "price"),
    }
    groups = _group_entities(entity_ids, metadata)
    result: list[str] = []
    for group in order[feature]:
        for entity_id in groups[group]:
            if entity_id not in result:
                result.append(entity_id)
    return result


def _combined_priority_entities(features: tuple[str, ...], entity_ids: EntityMap, metadata: EntityMetadataMap, *, limit: int) -> list[str]:
    """Return priority entities for multiple features."""
    result: list[str] = []
    for feature in features:
        for entity_id in _priority_entities(feature, entity_ids.get(feature, ()), metadata):
            if entity_id not in result:
                result.append(entity_id)
    return result[:limit]


def _overview_trend_entities(entity_ids: EntityMap, metadata: EntityMetadataMap) -> list[str]:
    """Return entities for the overview trend."""
    result: list[str] = []
    for feature in (FEATURE_SOLAR, FEATURE_GRID, FEATURE_BATTERY, FEATURE_CONTROLLABLE_LOADS):
        entity_id = _first_group(entity_ids, metadata, feature, "power")
        if entity_id:
            result.append(entity_id)
    return result[:6]


def _text(entity_id: str, metadata: EntityMetadata) -> str:
    """Return searchable text."""
    return " ".join(str(v) for v in (entity_id, metadata.get("friendly_name"), metadata.get("device_class"), metadata.get("unit")) if v).lower()


def _source(entity_id: str, metadata: EntityMetadata) -> str | None:
    """Infer compact source label."""
    text = _text(entity_id, metadata)
    for needle, label in (("solaredge", "SolarEdge"), ("solarman-pv1", "PV1"), ("solarman-pv2", "PV2"), ("solarman-pv3", "PV3"), ("solarman-pv4", "PV4"), ("alpha ess", "Alpha ESS"), ("zinvolt", "ZinVolt"), ("p1", "P1"), ("passat", "Passat"), ("wasmachine", "Wasmachine"), ("droger", "Droger"), ("koelkast", "Koelkast"), ("vriezer", "Vriezer"), ("lava", "Lava")):
        if needle in text:
            return label
    return None


def _price_label(text: str) -> str | None:
    """Infer short tariff/cost labels from entity text."""
    if not any(word in text for word in ("prijs", "price", "tarief", "cost", "kosten", "volatiliteit", "piek", "beste")):
        return None

    if "prijsvolatiliteit" in text or "volatiliteit" in text:
        return "Volatiliteit"
    if "laagste" in text:
        return "Laagste vandaag"
    if "hoogste" in text:
        return "Hoogste vandaag"
    if "gemiddelde prijs vandaag" in text or ("gemiddelde" in text and "vandaag" in text):
        return "Gemiddelde vandaag"
    if "gemiddelde uurprijs huidig" in text or ("uurprijs" in text and "huidig" in text):
        return "Uurprijs nu"
    if "gemiddelde uurprijs volgend" in text or ("uurprijs" in text and "volgend" in text):
        return "Uurprijs straks"
    if "huidige prijs incl" in text:
        return "Prijs nu incl."
    if "huidige prijs" in text:
        return "Prijs nu"
    if "volgende prijs" in text:
        return "Prijs straks"

    if "beste prijsperiode actief" in text:
        return "Dalperiode actief"
    if "beste prijs start over" in text:
        return "Dalstart over"
    if "beste prijs start" in text:
        return "Dalstart"
    if "beste prijs einde" in text:
        return "Daleinde"
    if "beste prijs" in text:
        return "Dalperiode"

    if "piekprijsperiode actief" in text:
        return "Piek actief"
    if "piekprijs start over" in text:
        return "Piek over"
    if "piekprijs start" in text:
        return "Piek start"
    if "piekprijs einde" in text:
        return "Piek einde"
    if "piekprijs" in text:
        return "Piekperiode"

    if "dynamic energy cost" in text or "cost" in text or "kosten" in text:
        if any(word in text for word in ("export", "teruglever")):
            return "kosten teruglevering"
        if any(word in text for word in ("import", "afname", "netafname")):
            return "kosten afname"
        if any(word in text for word in ("laadvermogen", "charging", "laden")):
            return "laadkosten"
        return "kosten"

    if "tarief" in text:
        return "Tarief"
    if "prijs" in text or "price" in text:
        return "Prijs"
    return None


def _role(entity_id: str, metadata: EntityMetadata) -> str:
    """Infer compact role label."""
    text = _text(entity_id, metadata)
    price_label = _price_label(text)
    if price_label is not None:
        return price_label

    group = _entity_group(entity_id, metadata)
    if group == "soc":
        return "SOC"
    if group == "power":
        if any(w in text for w in ("charge", "laad", "laden")):
            return "laden"
        if any(w in text for w in ("discharge", "ontlaad", "ontladen")):
            return "ontladen"
        if any(w in text for w in ("import", "afname")):
            return "afname"
        if any(w in text for w in ("export", "teruglever")):
            return "teruglevering"
        return "vermogen"
    if group == "energy":
        if any(w in text for w in ("today", "vandaag")):
            return "vandaag"
        if any(w in text for w in ("charge", "laad", "laden")):
            return "laden"
        if any(w in text for w in ("discharge", "ontlaad", "ontladen")):
            return "ontladen"
        if any(w in text for w in ("import", "afname")):
            return "import"
        if any(w in text for w in ("export", "teruglever")):
            return "export"
        return "energie"
    if group == "control":
        return "status"
    return str(metadata.get("friendly_name") or entity_id)


def _short_name(entity_id: str, metadata: EntityMetadataMap) -> str:
    """Return a short display name."""
    item = metadata.get(entity_id, {})
    source = _source(entity_id, item)
    role = _role(entity_id, item)
    if source and role.lower() not in source.lower():
        return f"{source} {role}"
    return role.capitalize() if len(role) < 20 else role


def _entity_entry(entity_id: str, metadata: EntityMetadataMap) -> dict[str, str]:
    """Return a named entity entry."""
    return {"entity": entity_id, "name": _short_name(entity_id, metadata)}


def _tile(entity_id: str, name: str, icon: str) -> DashboardConfig:
    """Return a tile card."""
    return {"type": "tile", "entity": entity_id, "name": name, "icon": icon, "vertical": False}


def _trend_card(title: str, entity_ids: list[str]) -> DashboardConfig:
    """Return a smoother native trend card."""
    return {"type": "statistics-graph", "title": title, "chart_type": "line", "days_to_show": 1, "period": "5minute", "stat_types": ["mean"], "entities": entity_ids}


def _gauge_grid(title: str, entity_ids: list[str], metadata: EntityMetadataMap) -> DashboardConfig:
    """Return SOC gauges."""
    return {"type": "grid", "title": title, "columns": 2, "square": False, "cards": [{"type": "gauge", "entity": entity_id, "name": _short_name(entity_id, metadata), "min": 0, "max": 100, "severity": {"green": 50, "yellow": 20, "red": 0}} for entity_id in entity_ids[:6]]}


def _entities_card(title: str, entity_ids: list[str], metadata: EntityMetadataMap) -> DashboardConfig:
    """Return entities with compact names."""
    return {"type": "entities", "title": title, "show_header_toggle": False, "state_color": True, "entities": [_entity_entry(entity_id, metadata) for entity_id in entity_ids]}
