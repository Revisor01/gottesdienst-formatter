# Gottesdienst-Formatter für Boyens Medien

## What This Is

Web-Anwendung des ev.-luth. Kirchenkreises Dithmarschen, die Gottesdiensttermine aus ChurchDesk-APIs und Excel-Dateien in exakt formatierte Fließtexte für Boyens Medien umwandelt. Die Termine werden nach Datum sortiert, mit standardisierten Abkürzungen (Gd., P., Pn.) und im vorgegebenen Fließtext-Format ausgegeben.

## Core Value

Der Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar.

## Requirements

### Validated

- ✓ Excel-Upload mit Verarbeitung zu Fließtext — existing
- ✓ ChurchDesk-API-Anbindung für mehrere Organisationen — existing
- ✓ Sortierung nach Datum — existing
- ✓ Deutsche Datums-/Zeitformatierung (Sonnabend, 5. April / 9.30 Uhr) — existing
- ✓ Gottesdienst-Typ-Abkürzungen (Gd., Gd. m. A., Gd. m. T.) — existing
- ✓ Pastor-Titel-Formatierung (P., Pn.) — existing
- ✓ Standort-Extraktion mit Kirchennamen bei Mehrdeutigkeit — existing
- ✓ Web-Interface mit Download/Clipboard-Funktion — existing
- ✓ Docker-Deployment auf Produktionsserver — existing

### Active

- [ ] Formatierungs-Output exakt nach Boyens-Vorgabe (alle Abweichungen fixen)
- [ ] Code-Deduplizierung: Formatierungslogik zentralisieren (3x dupliziert)
- [ ] Saubere Erweiterbarkeit für weitere Kirchengemeinden (neue ChurchDesk-Orgs)
- [ ] Hardcoded API-Tokens aus Quellcode entfernen (→ Environment Variables)
- [ ] Automatisierte Tests für Formatierungsfunktionen
- [ ] Pastor-Formatierung konsolidieren (3 verschiedene Implementierungen)

### Out of Scope

- Andere Konfessionen (Katholisch, Freikirchlich, Neuapostolisch) — Kirchenkreis liefert nur ev.-luth. Daten
- Mobile App — Web-Interface reicht
- Automatischer E-Mail-Versand an Boyens — manuelle Übermittlung genügt
- Mehrsprachigkeit — nur Deutsch relevant

## Context

- **Auftraggeber-Vorgabe**: Boyens Medien (Chefredakteur Johannes Simonsen) hat ein exaktes Fließtext-Format definiert, das ohne Nacharbeit ins Redaktionssystem übernommen werden kann
- **Formatvorgabe-Highlights**: Datum-Überschrift, dann Orte alphabetisch mit Uhrzeit, Typ, Pastor; bei mehreren Kirchen pro Ort den Kirchennamen angeben; spezielle Titel wie Diakon, Prädikantin, R. neben P./Pn.
- **Bestehender Code**: Funktioniert grundsätzlich, aber dreifach duplizierte Formatierungslogik, hardcoded API-Tokens, keine Tests
- **Codebase-Map**: Siehe `.planning/codebase/` für detaillierte Analyse
- **Erweiterung geplant**: Weitere Kirchengemeinden mit eigenen ChurchDesk-Instanzen werden hinzukommen

## Constraints

- **Formatierung**: Output muss exakt der Boyens-Vorgabe entsprechen — Abweichungen führen zur Nicht-Veröffentlichung
- **Tech Stack**: Python/Flask — bestehende Infrastruktur beibehalten
- **Deployment**: Docker auf 185.248.143.234, URL http://gd.kkd-fahrtenbuch.de
- **Datenquelle**: ChurchDesk API v3.0.0 — Struktur der API-Responses ist gegeben

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Nur ev.-luth. Termine | Kirchenkreis liefert nur eigene Daten, andere Konfessionen separat | — Pending |
| Brownfield-Stabilisierung vor Features | Code muss sauber sein bevor weitere APIs dazukommen | — Pending |
| Boyens-Fließtext als Referenzformat | Offizielle Vorgabe vom Chefredakteur, nicht verhandelbar | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-21 after initialization*
