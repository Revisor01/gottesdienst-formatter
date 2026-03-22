# Gottesdienst-Formatter für Boyens Medien

## What This Is

Web-Anwendung des ev.-luth. Kirchenkreises Dithmarschen, die Gottesdiensttermine aus ChurchDesk-APIs in exakt formatierte Fließtexte für Boyens Medien umwandelt und automatisch per E-Mail verschickt. Mit Login, Benutzerverwaltung, Personen-DB für Titel-Lookup und Settings-Seite zur Konfiguration.

## Core Value

Der Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar.

## Requirements

### Validated

- ✓ ChurchDesk-API-Anbindung für mehrere Organisationen — existing
- ✓ Sortierung nach Datum — existing
- ✓ Deutsche Datums-/Zeitformatierung (Sonnabend, kein führendes Null) — existing
- ✓ Gottesdienst-Typ-Abkürzungen (Gd., Gd. m. A., Konfirmation, etc.) — v1.0
- ✓ Standort-Extraktion mit Multi-Church-Logik — v1.0
- ✓ Formatierungslogik zentralisiert in web/formatting.py — v1.0
- ✓ Unit-Tests + Goldstandard-Fixture — v1.0
- ✓ GitHub Actions CI/CD + Watchtower Auto-Deploy — v1.0
- ✓ App Factory Pattern + SQLite-Datenbank — v2.0
- ✓ Login mit Benutzerverwaltung (Flask-Login, 30-Tage-Sessions) — v2.0
- ✓ Admin kann User anlegen/bearbeiten/deaktivieren — v2.0
- ✓ Health-Check Endpoint /health — v2.0
- ✓ Grünes Tailwind CSS Interface (Sidebar-Dashboard) — v2.0
- ✓ Excel-Import entfernt (nur noch ChurchDesk-API) — v2.0
- ✓ Vorschau mit Warnungen im Web-Interface — v2.0
- ✓ Settings-Seite mit SMTP-Konfiguration pro User (Fernet-verschlüsselt) — v2.0
- ✓ Automatischer monatlicher E-Mail-Versand (APScheduler, Wochenend-Logik) — v2.0
- ✓ Org-Verwaltung in der DB (Admin-CRUD, nicht ENV) — v2.0
- ✓ Pastor-Titel per DB-Lookup (Nachname → Titel, Regex-Fallback) — v2.0
- ✓ Custom Gottesdienst-Typ-Zuordnungen (Admin-konfigurierbar) — v2.0

### Active

(Keine aktiven Requirements — nächster Milestone definiert neue)

### Out of Scope

- Andere Konfessionen (Kath., Freikirchlich, Neuapostolisch) — Kirchenkreis liefert nur ev.-luth. Daten
- Mobile App — Web-Interface genügt
- Mehrsprachigkeit — nur Deutsch relevant
- OAuth / Social Login — Flask-Login mit Passwort reicht
- Celery / Redis — APScheduler in-process genügt
- PostgreSQL — SQLite reicht für <20 User

## Context

- **v1.0 shipped:** Stabilisierung, Formatierung, CI/CD Pipeline
- **v2.0 shipped:** App Factory, Login, Tailwind UI, Settings, Auto-Mail, Org-DB, Personen-DB
- **Tech Stack:** Python 3.11, Flask, SQLAlchemy + SQLite, Tailwind CSS, Gunicorn, Docker + Watchtower
- **Codebase:** ~3.200 LOC Python, 112+ Tests, 96 files
- **Server:** 185.248.143.234, automatisches Deployment via GitHub Actions → ghcr.io → Watchtower

## Constraints

- **Formatierung**: Output muss exakt der Boyens-Vorgabe entsprechen
- **Tech Stack**: Python/Flask + SQLite — beibehalten
- **Deployment**: Docker auf 185.248.143.234, automatisch via Watchtower
- **Farbe**: Grün als UI-Primärfarbe

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Boyens-Fließtext als Referenzformat | Offizielle Vorgabe vom Chefredakteur | ✓ Good |
| SQLite statt PostgreSQL | <20 User, kein Overhead nötig | ✓ Good |
| Tailwind CSS statt Bootstrap | Modern, Utility-First, kleiner Output | ✓ Good |
| smtplib statt Flask-Mail | Per-User SMTP-Settings aus DB, nicht global | ✓ Good |
| APScheduler in-process | Monatlicher Job, kein Celery/Redis Overhead | ✓ Good |
| Orgs in DB statt ENV | Eine Quelle der Wahrheit, Admin-verwaltbar | ✓ Good |
| Pastor-DB-Lookup statt Regex | Ehepaare disambiguierbar, Admin-pflegbar | ✓ Good |
| Strikt Boyens: keine Untertitel | Nur Typ-Abkürzung, keine Sonderformat-Texte | ✓ Good |
| Weltgebetstagsteam ausschreiben | User-Entscheidung | ✓ Good |
| Prä. für Prädikant/in | Kürzere Abkürzung, User-Entscheidung | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-03-22 after v2.0 milestone completion*
