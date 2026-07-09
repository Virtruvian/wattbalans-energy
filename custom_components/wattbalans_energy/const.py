"""Constants for WattBalans Energy Management."""

DOMAIN = "wattbalans_energy"
NAME = "WattBalans Energy Management"

CONF_FEATURES = "features"
CONF_ENTITIES = "entities"

FEATURE_SOLAR = "solar"
FEATURE_GRID = "grid"
FEATURE_BATTERY = "battery"
FEATURE_EV_CHARGING = "ev_charging"
FEATURE_DYNAMIC_TARIFF = "dynamic_tariff"
FEATURE_CONTROLLABLE_LOADS = "controllable_loads"

DEFAULT_FEATURES = {
    FEATURE_SOLAR: True,
    FEATURE_GRID: True,
    FEATURE_BATTERY: False,
    FEATURE_EV_CHARGING: False,
    FEATURE_DYNAMIC_TARIFF: False,
    FEATURE_CONTROLLABLE_LOADS: False,
}
