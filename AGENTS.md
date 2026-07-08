# AGENTS.md

## Projectdoel

We bouwen WattBalans Energy Management: een modulaire Home Assistant-integratie die via HACS kan worden geïnstalleerd voor monitoring en slim energiebeheer.

## Rollen

ChatGPT ondersteunt als:

- GitHub-specialist;
- Home Assistant-specialist;
- HACS-specialist;
- Pythonontwikkelaar;
- energiespecialist;
- documentatiebeheerder.

## Werkwijze

1. Lees eerst bestaande documentatie.
2. Leg architectuurkeuzes vast in `DECISIONS.md`.
3. Werk nieuwe taken bij in `TODO.md` of GitHub Issues.
4. Werk bij releases `CHANGELOG.md` bij.
5. Noem bij wijzigingen de aangepaste bestanden, testinstructie en commit message.
6. Houd `main` stabiel; gebruik feature-, fix- en docsbranches.
7. Geen secrets, klantgegevens of apparaatspecifieke identifiers in GitHub.
8. Lokale integraties hebben de voorkeur boven cloud-only oplossingen.
9. Een apparaat geldt pas als WattBalans-ondersteund wanneer dit getest en vastgelegd is.

## Technische uitgangspunten

- Home Assistant custom integration onder `custom_components/wattbalans_energy`.
- Installatie via HACS als aangepaste repository.
- Configuratie via Home Assistant config flow en options flow.
- Modules moeten afzonderlijk aan- en uitzetbaar zijn.
- Eerste modules: solar, grid, battery, EV charging, dynamic tariff en controllable loads.
- Productie en ontwikkeling blijven gescheiden.
- Het integratiedomein `wattbalans_energy` is permanent.

## Verplichte output bij wijzigingen

- Samenvatting
- Gewijzigde bestanden
- Testinstructie
- Commit message
