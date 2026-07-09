# Changelog

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
