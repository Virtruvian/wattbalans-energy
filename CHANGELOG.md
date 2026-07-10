# Changelog

## 0.1.10

- Verbetert de korte labels voor dynamische prijzen, tarieven en kosten.
- Zet prijsentiteiten om naar duidelijke namen zoals `Prijs nu`, `Prijs straks`, `Laagste vandaag`, `Piek start` en `Dalperiode actief`.
- Herkent kostenentiteiten beter als afname-, teruglever- of laadkosten.

## 0.1.9

- Bouwt het dashboard opnieuw op rond het eerder ontworpen energie-regie concept.
- Maakt de hoofdpagina `Regie` met een flowchart voor aanwezige onderdelen.
- Maakt subpagina's per onderdeel: zon, net, batterij, EV, kosten en slimme apparaten.
- Houdt de modulepagina's compacter met belangrijkste waarden, trends, energie, kosten en bediening.

## 0.1.8

- Verkort entiteitnamen in tegels en lijsten zodat labels leesbaarder worden.
- Vervangt ruwe history-grafieken door vloeiendere statistics-grafieken met gemiddelden per 5 minuten.
- Richt de overzichtspagina opnieuw in met KPI's, samenvattingsblokken en een compacte trendgrafiek.
- Haalt de drukke pseudo-energy-flow uit de native fallback en maakt ruimte voor een betere optionele flowkaart later.

## 0.1.7

- Voegt een SEM-inspired overzichtspagina toe met KPI-tegels, energiestroom en compacte moduleblokken.
- Gebruikt native Lovelace tile-, grid-, markdown-, gauge-, history-graph- en entities-kaarten zonder verplichte custom cards.
- Maakt de eerste energiestroom visueel met blokken voor zon, huis, net, accu, EV, verbruikers en opslag.
- Verhoogt de managed dashboardversie zodat het WattBalans-dashboard opnieuw wordt opgebouwd.

## 0.1.6

- Bouwt slimmere dashboardkaarten op basis van entity metadata.
- Groepeert entities automatisch in laadniveau, vermogen, energie, tarieven en status/bediening.
- Voegt history-graph kaarten toe voor vermogensentities.
- Voegt gauge-kaarten toe voor SOC/laadniveau.
- Maakt het overzicht compacter met module-aantallen en relevante samenvattingskaarten.

## 0.1.5

- Gebruikt de bestaande Home Assistant Energy Dashboard-configuratie als sterke bron voor automatische entity-suggesties.
- Neemt solar-, grid- en batterijbronnen uit het Energy Dashboard over als voorgeselecteerde WattBalans-entiteiten wanneer ze beschikbaar zijn.
- Neemt bekende apparaatverbruikers uit het Energy Dashboard mee als voorstel voor schakelbare/verbruikersmodules.
- Houdt trefwoorddetectie als aanvullende fallback naast de Energy Dashboard-configuratie.

## 0.1.4

- Maakt automatische batterijherkenning selectiever.
- Sluit kleine apparaatbatterijen van dimmers, sensoren, Nuki en remotes beter uit.
- Herkent thuisaccu's sterker via signalen zoals Alpha ESS, Zinvolt, thuisaccu, SOC, charge/discharge en omvormer/inverter.
- Houdt automatische herkenning als voorstel dat handmatig gecontroleerd en aangepast moet worden.

## 0.1.3

- Voegt automatische entity-herkenning toe voor geselecteerde modules.
- Vervangt losse rolvelden door multi-entity-selectors per module.
- Ondersteunt meerdere zonnepanelen-, batterij-, EV- en verbruikerssystemen per module.
- Lost validatiefouten op die ontstonden door lege entity-selectors.

## 0.1.2

- Voegt optionele entity-selectie per module toe.
- Geeft gekoppelde entity IDs door aan het automatisch dashboard.

## 0.1.1

- Lost compatibiliteit met frontend panelregistratie op.

## 0.1.0

- Eerste HACS-testversie met modulekeuze, diagnostische entiteiten en dashboardbasis.
