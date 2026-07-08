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

## Automatisch dashboard

WattBalans krijgt na configuratie automatisch een eigen Home Assistant-dashboard, vergelijkbaar met SEM Community.

Het dashboard wordt modulair opgebouwd op basis van de gekozen onderdelen. Een installatie zonder thuisbatterij of EV-laadpunt krijgt dus geen lege batterij- of EV-pagina's.

De huidige basisgenerator maakt:

- altijd een algemeen overzicht;
- een aparte view voor zonnepanelen en netaansluiting wanneer geselecteerd;
- optionele views voor batterij en EV-laden;
- optionele views voor dynamische tarieven en schakelbare verbruikers;
- entiteitskaarten wanneer de bijbehorende Home Assistant-entiteiten bekend zijn;
- een duidelijke tijdelijke melding zolang een module nog geen gekoppelde entiteiten heeft.

**Huidige status:** de modulaire Lovelace-configuratiegenerator is aanwezig. Automatisch registreren en veilig synchroniseren met Home Assistant-opslag volgt als afzonderlijke managerlaag.

## Status

Alphafase. De huidige versie bevat een Home Assistant-integratie met config flow, options flow, conditioneel geladen modules, diagnostische module-entiteiten, HACS-structuur en een modulaire dashboardconfiguratiegenerator. De daadwerkelijke energiemodules en automatische dashboardregistratie volgen in de volgende ontwikkelfasen.

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

## Ontwikkeling

De hoofdontwikkeling vindt plaats in `Virtruvian/solar-project-v2`. Deze publieke repository is bedoeld als HACS-testrepository voor Home Assistant.

## Licentie

MIT. Zie `LICENSE`.
