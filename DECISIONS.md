# Architecture Decisions

## ADR-001 — Publieke HACS-testrepository

**Status:** accepted

`Virtruvian/wattbalans-energy` is de publieke repository waarmee de integratie in Home Assistant via HACS kan worden getest.

De hoofdontwikkeling blijft voorlopig in `Virtruvian/solar-project-v2`; deze publieke repository bevat de HACS-installeerbare testversie.

## ADR-002 — Permanent integratiedomein

**Status:** accepted

Het Home Assistant-domein is permanent:

```text
wattbalans_energy
```

De zichtbare productnaam is `WattBalans Energy Management`.

## ADR-003 — SEM Community als technische referentie

**Status:** accepted

`traktore-org/sem-community` wordt gebruikt als technische referentie en mogelijke bronbasis onder de MIT-licentie. De exacte upstream commit wordt vastgelegd voordat code wordt geïmporteerd.

## ADR-004 — Modulaire componentselectie

**Status:** accepted

De integratie ondersteunt feature flags voor:

- solar;
- grid;
- battery;
- ev_charging;
- dynamic_tariff;
- controllable_loads.

Niet-geselecteerde modules mogen geen configuratiestappen, platforms, entiteiten of dashboardviews laden.

## ADR-005 — Beheerd WattBalans-dashboard

**Status:** accepted

De integratie maakt automatisch een Lovelace-dashboard aan met:

- titel: `WattBalans Energy`;
- pad: `wattbalans-energy`;
- zichtbaarheid in de Home Assistant-zijbalk.

De dashboardconfiguratie wordt opnieuw opgebouwd op basis van de geselecteerde modules. Een bestaand dashboard met hetzelfde pad wordt alleen overschreven wanneer het door WattBalans is gemarkeerd als beheerd dashboard.

Een bestaand niet-beheerd dashboard met hetzelfde pad wordt niet overschreven. Daarmee voorkomen we dat handmatige gebruikersdashboards stilzwijgend verdwijnen.

## ADR-006 — Optionele entity-selectie per module

**Status:** accepted

Per geselecteerde module kunnen optioneel Home Assistant-entiteiten worden gekoppeld. Deze entity IDs worden opgeslagen in de config entry data of options onder `entities`.

Uitgangspunten:

- entity-selectie is optioneel;
- lege velden blijven toegestaan;
- niet-geselecteerde modules krijgen geen entity-selectievelden;
- wijzigen via de options flow herlaadt de integratie;
- het beheerde dashboard gebruikt gekoppelde entiteiten voor modulekaarten;
- ontbrekende entiteiten tonen nog steeds een tijdelijke modulemelding.

Deze laag koppelt bestaande Home Assistant-entiteiten aan WattBalans. De echte energielogica en automatische apparaatdetectie worden later toegevoegd.
