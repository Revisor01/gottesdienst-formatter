---
phase: 01-stabilisierung
plan: 01
subsystem: formatting-config
tags: [refactor, security, deduplication, formatting, config]
dependency_graph:
  requires: []
  provides: [web/formatting.py, web/config.py]
  affects: [web/app.py, web/churchdesk_api.py]
tech_stack:
  added: []
  patterns: [env-var-config, single-source-of-truth, module-extraction]
key_files:
  created:
    - web/formatting.py
    - web/config.py
  modified:
    - web/app.py
decisions:
  - "format_pastor basiert auf format_boyens_pastor-Logik (vollstaendig), nicht der simplen app.py-Variante"
  - "ORGANIZATIONS-Fallback-Dict ist leer wenn CHURCHDESK_ORG_IDS nicht gesetzt (SEC-01 Anforderung)"
  - "Secret Key nutzt os.getenv('SECRET_KEY') or secrets.token_hex(32) — kein RuntimeError bei fehlendem Env-Var"
metrics:
  duration: 132s
  completed: 2026-03-22
  tasks: 3
  files: 3
requirements:
  - SEC-01
  - SEC-02
  - CODE-01
  - CODE-02
  - CODE-03
---

# Phase 01 Plan 01: Zentrale Module Formatierung und Konfiguration Summary

**One-liner:** Dreifach duplizierte Formatierungslogik in web/formatting.py zentralisiert, hardcoded API-Tokens durch env-var-basierte web/config.py ersetzt, app.py von 95 Duplikat-Zeilen befreit.

## What Was Built

Zwei neue Module extrahiert und app.py bereinigt:

1. **web/formatting.py** — Einzige Quelle der Wahrheit fuer alle format_*-Funktionen
   - `format_date()`, `format_time()`, `format_service_type()` aus app.py extrahiert
   - `format_pastor()` basiert auf der vollstaendigen `format_boyens_pastor()`-Logik aus churchdesk_api.py (Delimiter-Splitting, Dn./D./Ps./Praedikant-Unterstuetzung, Sonderfaelle)

2. **web/config.py** — Env-Var-basierte Organisationskonfiguration
   - `load_organizations()` laedt alle Org-Daten aus `CHURCHDESK_ORG_IDS` und `CHURCHDESK_ORG_{ID}_TOKEN/NAME`-Vars
   - Keine hardcoded Tokens mehr im Quellcode

3. **web/app.py** — Bereinigt
   - 95 Zeilen duplizierter Formatierungsfunktionen entfernt
   - Imports auf formatting.py und config.py umgestellt
   - Secret Key: `os.getenv('SECRET_KEY') or secrets.token_hex(32)`
   - Index-Route uebergibt `organizations=ORGANIZATIONS` ans Template

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | web/formatting.py erstellen | 1dd2536 | web/formatting.py (neu, 145 Zeilen) |
| 2 | web/config.py erstellen | e42e558 | web/config.py (neu, 38 Zeilen) |
| 3 | web/app.py bereinigen | ac3dd33 | web/app.py (-95 Zeilen netto) |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - alle Funktionen sind vollstaendig implementiert. Die `organizations=ORGANIZATIONS`-Variable im Template wird leer sein wenn die Env-Vars nicht gesetzt sind (beabsichtigt per SEC-01), wird in Plan 02 verdrahtet.

## Self-Check: PASSED

Files created:
- web/formatting.py: FOUND
- web/config.py: FOUND

Commits:
- 1dd2536: FOUND
- e42e558: FOUND
- ac3dd33: FOUND
