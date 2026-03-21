---
phase: 01-stabilisierung
plan: 02
subsystem: web
tags: [security, refactoring, configuration, templates]
dependency_graph:
  requires: [01-01]
  provides: [SEC-01, CODE-03, CODE-04]
  affects: [web/churchdesk_api.py, web/docker-compose.yml, web/templates/index.html, gottesdienst_formatter_final.py]
tech_stack:
  added: []
  patterns: [env-var-based-config, dynamic-jinja2-templates, single-module-imports]
key_files:
  created: [.env.example]
  modified:
    - web/churchdesk_api.py
    - web/docker-compose.yml
    - web/templates/index.html
    - web/.env.example
    - gottesdienst_formatter_final.py
decisions:
  - "web/.env.example mit hardcoded Token gefunden und mitbereinigt (Rule 1 - Security Bug)"
  - "format_pastor wird nicht in churchdesk_api.py aufgerufen (Aufruf liegt in app.py) — Import trotzdem korrekt"
metrics:
  duration: 196s
  completed: "2026-03-21T23:05:21Z"
  tasks_completed: 2
  files_changed: 5
---

# Phase 01 Plan 02: Consumer-Migration und Token-Bereinigung Summary

Alle verbleibenden Consumer auf die in Plan 01 erstellten Module umgestellt und saemtliche hardcoded API-Credentials aus dem Quellcode entfernt.

## What Was Built

### Task 1: churchdesk_api.py bereinigen

`web/churchdesk_api.py` importiert jetzt `ORGANIZATIONS` aus `config.py` und `format_pastor` aus `formatting.py` statt eigene Definitionen zu enthalten.

Entfernt:
- Das hardcoded `ORGANIZATIONS`-Dict mit 5 API-Tokens (275 Zeichen Tokens)
- Die `def format_boyens_pastor()` Funktion (65 Zeilen)
- Den Kommentar "default token for org 2596" aus `create_api_client()`

**Commit:** `4a7b1cf`

### Task 2: docker-compose.yml, index.html, .env.example, Standalone-Script

**docker-compose.yml:** Environment-Block ersetzt — `CHURCHDESK_ORG_*` Env-Vars statt hardcoded Token-Fallbacks. `SECRET_KEY` hinzugefuegt.

**index.html:** Hardcoded 4-Checkbox-Block durch dynamisches Jinja2-Template ersetzt. Neue Orgs erfordern nur neue Env-Vars — kein Code-Change.

**.env.example (root):** Neu erstellt mit vollstaendiger Dokumentation aller benoetigten Env-Vars. Alle TOKEN-Zeilen leer (kein Geheimnis im Repo).

**gottesdienst_formatter_final.py:** `sys.path.insert` + `from formatting import` statt eigener Kopien der 4 Formatierungsfunktionen.

**Commit:** `806d933`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Security Bug] web/.env.example mit hardcoded Token bereinigt**
- **Found during:** Task 2 finale Verifikation
- **Issue:** `web/.env.example` aus Juli 2025 enthielt noch `CHURCHDESK_API_TOKEN=d4ec66780546786c92b916f873ee713181c1b695d32e7ba9839e760eaecd3fa1`
- **Fix:** web/.env.example auf neues Format umgestellt, Token entfernt
- **Files modified:** `web/.env.example`
- **Commit:** `806d933` (im selben Commit wie Task 2)

## Success Criteria Check

- [x] Keine API-Tokens oder Secret Keys im Quellcode — alle kommen aus Env-Vars
- [x] Formatierungslogik existiert genau einmal in `web/formatting.py`
- [x] Neue ChurchDesk-Org: nur neue Env-Vars noetig — kein Code-Change
- [x] Genau eine `format_pastor()`-Funktion in `formatting.py`
- [x] `.env.example` dokumentiert alle benoetigten Env-Vars

## Known Stubs

Keine — alle Org-Checkboxen werden dynamisch aus `organizations`-Template-Variable generiert, die von `app.py` uebergeben wird (via `ORGANIZATIONS` aus `config.py`).

## Self-Check: PASSED
