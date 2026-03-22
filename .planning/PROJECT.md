# Gottesdienst-Formatter für Boyens Medien

## What This Is

Web-Anwendung des ev.-luth. Kirchenkreises Dithmarschen, die Gottesdiensttermine aus ChurchDesk-APIs in exakt formatierte Fließtexte für Boyens Medien umwandelt und automatisch per E-Mail verschickt. Mit Login, Benutzerverwaltung und Settings-Seite zur Konfiguration.

## Core Value

Der Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar.

## Current Milestone: v2.0 — App Relaunch

**Goal:** Aus dem Formatter-Tool eine vollwertige Web-App machen: modernes UI, Login, Settings, automatische Mail, Excel-Import raus.

**Target features:**
- Excel-Import entfernen (nur noch ChurchDesk-API)
- Web-Interface Makeover (Grün als Farbe)
- Login mit Benutzerverwaltung (mehrere User)
- Settings-Seite (Org-Verwaltung, Mail-Einstellungen pro User)
- Automatische E-Mail an Boyens (konfigurierbar pro User, nicht ENV)
- Sonderformat-Titel besser parsen
- Vorschau im Web-Interface mit Warnungen
- Health-Check Endpoint

## Requirements

### Validated

- ✓ ChurchDesk-API-Anbindung für mehrere Organisationen — existing
- ✓ Sortierung nach Datum — existing
- ✓ Deutsche Datums-/Zeitformatierung — existing
- ✓ Gottesdienst-Typ-Abkürzungen — existing
- ✓ Pastor-Titel-Formatierung — existing
- ✓ Standort-Extraktion mit Kirchennamen — existing
- ✓ Web-Interface mit Download/Clipboard — existing
- ✓ Docker-Deployment mit CI/CD — v1.0
- ✓ Formatierungslogik zentralisiert in web/formatting.py — v1.0
- ✓ ENV-basierte Konfiguration — v1.0
- ✓ Formatierungs-Output exakt nach Boyens-Vorgabe — v1.0
- ✓ Unit-Tests + Goldstandard-Fixture — v1.0
- ✓ GitHub Actions CI/CD + Watchtower — v1.0

### Active

(Defined in REQUIREMENTS.md for v2.0)

### Out of Scope

- Andere Konfessionen (Kath., Freikirchlich, Neuapostolisch) — Kirchenkreis liefert nur ev.-luth. Daten
- Mobile App — Web-Interface genügt
- Mehrsprachigkeit — nur Deutsch relevant
- Excel-Import — wird in v2.0 entfernt, nur noch ChurchDesk-API

## Context

- **v1.0 abgeschlossen**: Stabilisierung, Formatierung, CI/CD Pipeline — alles läuft
- **Auftraggeber**: Boyens Medien, Fließtext-Format ist Pflicht
- **Infrastruktur**: Docker + Watchtower auf 185.248.143.234, automatisches Deployment via GitHub Actions
- **Neue Anforderung v2.0**: Aus Tool eine echte App machen — Login, Settings, automatische Mail
- **Design**: Grün als Farbe gesetzt
- **Mail-Konfiguration**: Pro User in Settings, NICHT in ENV-Vars
- **Datenbank nötig**: Für User-Accounts und Settings (SQLite oder PostgreSQL)

## Constraints

- **Formatierung**: Output muss exakt der Boyens-Vorgabe entsprechen
- **Tech Stack**: Python/Flask — beibehalten, erweitern um DB
- **Deployment**: Docker auf 185.248.143.234, automatisch via Watchtower
- **Farbe**: Grün ist gesetzt für das UI

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Nur ev.-luth. Termine | Kirchenkreis liefert nur eigene Daten | ✓ Good |
| Boyens-Fließtext als Referenzformat | Offizielle Vorgabe vom Chefredakteur | ✓ Good |
| Excel-Import entfernen | Alles kommt aus ChurchDesk-API, Excel war Legacy | — v2.0 |
| Mail-Settings pro User, nicht ENV | Flexibler, mehrere User möglich | — v2.0 |
| Grün als UI-Farbe | User-Entscheidung | — v2.0 |
| Login + Benutzerverwaltung | Mehrere User sollen das Tool nutzen können | — v2.0 |

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
*Last updated: 2026-03-22 after milestone v2.0 start*
