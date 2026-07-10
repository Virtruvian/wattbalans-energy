"""Naming and role helpers for WattBalans Energy Management."""

from __future__ import annotations

from typing import Any

EntityMetadata = dict[str, str | None]
EntityMetadataMap = dict[str, EntityMetadata]


def entity_text(entity_id: str, metadata: EntityMetadata | None = None) -> str:
    """Return searchable text for an entity."""
    metadata = metadata or {}
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


def entity_group(entity_id: str, metadata: EntityMetadata | None = None) -> str:
    """Return the best WattBalans role group for an entity."""
    metadata = metadata or {}
    text = entity_text(entity_id, metadata)
    device_class = metadata.get("device_class")
    unit = str(metadata.get("unit") or "").lower()
    domain = metadata.get("domain") or entity_id.split(".", 1)[0]

    if price_label(text) is not None:
        return "price"
    if battery_label(text) is not None:
        if any(word in text for word in ("soc", "state of charge", "%")) or unit == "%":
            return "soc"
        if any(word in text for word in ("capacity", "capaciteit")):
            return "energy"
    if "soc" in text or unit == "%" or device_class == "battery":
        return "soc"
    if device_class == "monetary" or any(
        word in text for word in ("tarief", "price", "prijs", "cost", "kosten")
    ):
        return "price"
    if device_class == "power" or unit in {"w", "kw"}:
        return "power"
    if device_class == "energy" or unit in {"wh", "kwh"}:
        return "energy"
    if domain in {"switch", "binary_sensor"}:
        return "control"
    return "other"


def source_label(entity_id: str, metadata: EntityMetadata | None = None) -> str | None:
    """Infer a compact source label."""
    text = entity_text(entity_id, metadata)
    for needle, label in (
        ("solaredge", "SolarEdge"),
        ("solarman-pv1", "PV1"),
        ("solarman-pv2", "PV2"),
        ("solarman-pv3", "PV3"),
        ("solarman-pv4", "PV4"),
        ("alpha ess", "Alpha ESS"),
        ("alpha_ess", "Alpha ESS"),
        ("alphaess", "Alpha ESS"),
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


def battery_label(text: str) -> str | None:
    """Infer short battery labels from entity text."""
    if not any(
        word in text
        for word in (
            "accu",
            "battery",
            "batterij",
            "alpha ess",
            "alpha_ess",
            "alphaess",
            "zinvolt",
            "soc",
            "capacity",
            "capaciteit",
            "charge",
            "discharge",
            "laad",
            "ontlaad",
        )
    ):
        return None

    if "laagste" in text and "soc" in text:
        return "Laagste SOC"
    if "gemiddelde" in text and "soc" in text:
        return "Gemiddelde SOC"
    if "soc" in text or "state of charge" in text:
        return "SOC"
    if "capacity" in text or "capaciteit" in text:
        return "capaciteit"
    if any(word in text for word in ("discharge", "ontladen", "ontlaad")):
        if any(word in text for word in ("energy", "energie", "kwh")):
            return "ontladen"
        return "ontlaadvermogen"
    if any(word in text for word in ("charge", "laden", "laad")):
        if any(word in text for word in ("energy", "energie", "kwh")):
            return "laden"
        return "laadvermogen"
    if "power" in text or "vermogen" in text:
        return "vermogen"
    return None


def price_label(text: str) -> str | None:
    """Infer short tariff/cost labels from entity text."""
    if not any(
        word in text
        for word in ("prijs", "price", "tarief", "cost", "kosten", "volatiliteit", "piek", "beste")
    ):
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


def role_label(entity_id: str, metadata: EntityMetadata | None = None) -> str:
    """Infer a compact role label."""
    metadata = metadata or {}
    text = entity_text(entity_id, metadata)

    price = price_label(text)
    if price is not None:
        return price

    battery = battery_label(text)
    if battery is not None:
        return battery

    group = entity_group(entity_id, metadata)
    if group == "soc":
        return "SOC"
    if group == "power":
        if any(word in text for word in ("charge", "laad", "laden")):
            return "laden"
        if any(word in text for word in ("discharge", "ontlaad", "ontladen")):
            return "ontladen"
        if any(word in text for word in ("import", "afname")):
            return "afname"
        if any(word in text for word in ("export", "teruglever")):
            return "teruglevering"
        return "vermogen"
    if group == "energy":
        if any(word in text for word in ("today", "vandaag")):
            return "vandaag"
        if any(word in text for word in ("charge", "laad", "laden")):
            return "laden"
        if any(word in text for word in ("discharge", "ontlaad", "ontladen")):
            return "ontladen"
        if any(word in text for word in ("import", "afname")):
            return "import"
        if any(word in text for word in ("export", "teruglever")):
            return "export"
        return "energie"
    if group == "control":
        return "status"
    return str(metadata.get("friendly_name") or entity_id)


def friendly_label(entity_id: str, metadata: EntityMetadata | None = None) -> str:
    """Return a short WattBalans display name for an entity."""
    metadata = metadata or {}
    text = entity_text(entity_id, metadata)
    source = source_label(entity_id, metadata)
    role = role_label(entity_id, metadata)

    if role in {"Laagste SOC", "Gemiddelde SOC"}:
        return role
    if source and role.lower() not in source.lower():
        return f"{source} {role}"
    if source:
        return source
    return role.capitalize() if len(role) < 24 else role


def metadata_from_state(entity_id: str, state: Any) -> EntityMetadata:
    """Build naming metadata from a Home Assistant state object."""
    return {
        "device_class": state.attributes.get("device_class") if state else None,
        "domain": entity_id.split(".", 1)[0],
        "friendly_name": state.attributes.get("friendly_name") if state else None,
        "state_class": state.attributes.get("state_class") if state else None,
        "unit": state.attributes.get("unit_of_measurement") if state else None,
    }
