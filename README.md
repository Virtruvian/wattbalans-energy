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

## Entity-selectie

Na het kiezen van de modules kan per onderdeel een set Home Assistant-entiteiten worden gekoppeld. Deze velden zijn optioneel en kunnen later via **Opties** worden aangepast.

Voorbeelden:

- zonnepanelen: huidig vermogen, opbrengst vandaag en totaalopbrengst;
- netaansluiting: huidig vermogen, afname totaal en teruglevering totaal;
- batterij: laadniveau, laad-/ontlaadvermogen en energieteller;
- EV-laden: laadvermogen, geladen energie en status;
- dynamische tarieven: huidige en volgende prijs;
- schakelbare verbruikers: vermogen en schakelaar.

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

## Status

Alphafase. De huidige versie bevat een Home Assistant-integratie met config flow, options flow, conditioneel geladen modules, optionele entity-selectie, diagnostische module-entiteiten, HACS-structuur, een modulaire dashboardconfiguratiegenerator en een eerste dashboardmanager. De daadwerkelijke energiemodules volgen in de volgende ontwikkelfasen.

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
10. Koppel eventueel de bijbehorende Home Assistant-entiteiten.
11. Open daarna het dashboard **WattBalans Energy** in de zijbalk.

## Ontwikkeling

De hoofdontwikkeling vindt plaats in `Virtruvian/solar-project-v2`. Deze publieke repository is bedoeld als HACS-testrepository voor Home Assistant.

## Licentie

MIT. Zie `LICENSE`.
