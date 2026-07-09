# WattBalans Energy Management

Modulaire Home Assistant-integratie voor monitoring en slim energiebeheer binnen WattBalans.

## Oorsprong van het project

WattBalans Energy Management is gebaseerd op en geïnspireerd door de open-source repository `traktore-org/sem-community`.

SEM Community vormt de technische referentie en mogelijke bronbasis voor onder andere energiestromen, hardwaredetectie, batterij- en EV-logica en dashboardgeneratie. WattBalans ontwikkelt hierop een eigen integratie met een eigen domein, configuratieflow, componentselectie, dashboardopbouw, compatibiliteitsbeleid en releasecyclus.

De oorspronkelijke repository gebruikt de MIT-licentie. Bij het overnemen of aanpassen van code blijven de vereiste oorspronkelijke copyright- en licentievermeldingen behouden.

## Doel

De integratie wordt via HACS installeerbaar en ondersteunt op termijn optionele modules voor:

- zonnepanelen;
- netmeting;
- thuisbatterijen;
- EV-laden;
- dynamische energietarieven;
- schakelbare verbruikers.

## Automatische herkenning en entity-selectie

Na het kiezen van de modules probeert WattBalans relevante Home Assistant-entiteiten automatisch te herkennen op basis van entity ID, naam, device class, state class en meeteenheid.

De automatische herkenning is bedoeld als voorstel. De selectie blijft handmatig aanpasbaar via de configuratieflow en via **Opties**.

Per module kunnen meerdere entiteiten worden geselecteerd. Daardoor ondersteunt de basis meerdere zonnepaneleninstallaties, meerdere omvormers, meerdere batterijsystemen en meerdere laadpunten.

Voorbeelden:

- zonnepanelen: alle relevante solar-, PV-, omvormer- en opbrengstentiteiten;
- netaansluiting: P1-, grid-, import- en exportentiteiten;
- batterij: SOC-, laadvermogen-, ontlaadvermogen- en accu-entiteiten;
- EV-laden: laadvermogen, geladen energie en status;
- dynamische tarieven: huidige en volgende prijs;
- schakelbare verbruikers: vermogen en schakelaars.

## Automatisch dashboard

WattBalans krijgt na configuratie automatisch een eigen Home Assistant-dashboard, vergelijkbaar met SEM Community.

Het dashboard wordt modulair opgebouwd op basis van de gekozen onderdelen. Een installatie zonder thuisbatterij of EV-laadpunt krijgt dus geen lege batterij- of EV-pagina's.

De huidige dashboardmanager:

- maakt automatisch het dashboard `WattBalans Energy` aan;
- gebruikt het pad `wattbalans-energy`;
- toont het dashboard in de Home Assistant-zijbalk;
- maakt altijd een algemeen overzicht;
- maakt alleen views voor geselecteerde modules;
- vult moduleviews met gekoppelde Home Assistant-entiteiten wanneer die zijn opgegeven;
- werkt het beheerde dashboard opnieuw bij na een wijziging in de options flow;
- weigert een bestaand dashboard met hetzelfde pad te overschrijven wanneer dit niet door WattBalans is aangemaakt.

## SEM-inspired overzicht

De overzichtspagina gebruikt een SEM-inspired structuur met:

- KPI-tegels voor actuele hoofdwaarden;
- een native Lovelace energiestroom met blokken voor zon, huis, net, accu, EV, verbruikers en opslag;
- compacte moduleblokken;
- grafieken voor vermogenswaarden;
- gauges voor SOC/laadniveau.

Deze eerste visuele laag gebruikt alleen standaard Home Assistant Lovelace-kaarten. Er zijn dus nog geen verplichte custom cards nodig. Later kunnen optioneel Mushroom, ApexCharts of een echte power-flow card worden ondersteund.

## Status

Alphafase. De huidige versie bevat een Home Assistant-integratie met config flow, options flow, conditioneel geladen modules, automatische entity-herkenning, optionele multi-entity-selectie, diagnostische module-entiteiten, HACS-structuur, een SEM-inspired dashboardconfiguratiegenerator en een eerste dashboardmanager. De daadwerkelijke energiemodules volgen in de volgende ontwikkelfasen.

## Installatie via HACS

1. Open HACS in Home Assistant.
2. Ga naar **Integraties**.
3. Kies rechtsboven **Aangepaste repositories**.
4. Voeg deze repository toe:

   `https://github.com/Virtruvian/wattbalans-energy`

5. Kies categorie **Integration**.
6. Installeer **WattBalans Energy Management**.
7. Herstart Home Assistant.
8. Voeg de integratie toe via **Instellingen → Apparaten en diensten**.
9. Selecteer de aanwezige onderdelen.
10. Controleer de automatisch voorgestelde entiteiten en pas deze eventueel aan.
11. Open daarna het dashboard **WattBalans Energy** in de zijbalk.

## Ontwikkeling

De hoofdontwikkeling vindt plaats in `Virtruvian/solar-project-v2`. Deze publieke repository is bedoeld als HACS-testrepository voor Home Assistant.

## Licentie

MIT. Zie `LICENSE`.
