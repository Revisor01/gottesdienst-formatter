---
phase: 05-ui-makeover-formatierung
plan: 02
subsystem: web/templates + web/main
tags: [cleanup, excel-removal, tailwind, templates]
dependency_graph:
  requires: ["05-01"]
  provides: ["clean-routes", "tailwind-templates"]
  affects: ["web/main/routes.py", "web/templates/index.html", "web/templates/result.html"]
tech_stack:
  added: []
  patterns: ["Tailwind component classes (btn-primary, card, alert-warning)", "Jinja2 template inheritance with base.html"]
key_files:
  created: []
  modified:
    - web/main/routes.py
    - web/requirements.txt
    - web/formatting.py
    - web/templates/index.html
    - web/templates/result.html
    - web/tests/test_formatting.py
    - web/tests/test_auth.py
    - web/tests/test_app_factory.py
decisions:
  - "format_service_type(None) returns 'Gd.' not '' — consistent with 'unknown service = standard service' semantics"
metrics:
  duration: ~10min
  completed: "2026-03-22T12:11:56Z"
  tasks_completed: 2
  files_modified: 8
---

# Phase 05 Plan 02: Excel-Entfernung und Tailwind Template-Redesign Summary

**One-liner:** Excel upload route, pandas/openpyxl dependencies entfernt; index.html und result.html auf Tailwind-Only-Layout mit Monospace-Vorschau umgestellt.

## What Was Done

### Task 1: Excel-Code entfernen (routes.py, requirements.txt, formatting.py)

- `upload_file()` Route aus `web/main/routes.py` entfernt — `/upload` liefert jetzt 404
- `process_excel_file()` Funktion aus `web/main/routes.py` entfernt
- `import pandas as pd`, `import tempfile`, `import os` aus routes.py entfernt (waren nur von Excel-Code genutzt)
- `pandas==2.3.1` und `openpyxl==3.1.5` aus `web/requirements.txt` entfernt
- `formatting.py`: `import pandas as pd` entfernt, `pd.isna()` durch `is None`/`not titel` ersetzt
- Tests angepasst: `pd.NaT`-Test-Cases durch `None`-Tests ersetzt, `/upload`-Route aus Auth-Tests entfernt

### Task 2: Tailwind-Redesign index.html und result.html

- `index.html` komplett neu geschrieben: nur ChurchDesk-API-Bereich, Tailwind-Klassen, dynamisches Jahr-Select via `current_year` aus Route
- `result.html` komplett neu geschrieben: Monospace-Vorschau (`font-mono`), prominente Copy/Download-Buttons, `warnings`-Loop mit `alert-warning`-Boxen
- Kein Bootstrap mehr in beiden Templates
- `routes.py index()`: übergibt jetzt `current_year=datetime.now().year` ans Template

## Commits

| Hash | Message |
|------|---------|
| 85639a8 | feat(05-02): remove Excel upload route and pandas dependency |
| e919aa1 | feat(05-02): redesign index.html and result.html with Tailwind |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test-Dateien für pd.NaT und /upload-Route angepasst**
- **Found during:** Task 1 Verifikation
- **Issue:** `test_formatting.py` importierte `pandas` und testete `pd.NaT` — nach Entfernung von pandas schlugen 3 Tests fehl. `test_auth.py` testete `/upload` Route auf Login-Redirect — Route ist jetzt 404. `test_app_factory.py` prüfte `main.upload_file` in routes — nicht mehr vorhanden.
- **Fix:** `pd.NaT` durch `None` in test_formatting.py ersetzt, `pandas`-Import entfernt; `/upload`-Eintrag aus test_auth.py Parameterliste entfernt; `main.upload_file`-Assertion aus test_app_factory.py entfernt.
- **Files modified:** web/tests/test_formatting.py, web/tests/test_auth.py, web/tests/test_app_factory.py
- **Commit:** 85639a8

**2. [Rule 2 - Missing functionality] current_year an index-Template übergeben**
- **Found during:** Task 2 Template-Umsetzung
- **Issue:** Plan sah dynamisches Jahr-Select vor — Template konnte `current_year` nicht aus dem Kontext beziehen ohne Route-Anpassung.
- **Fix:** `routes.py index()` gibt jetzt `current_year=datetime.now().year` mit; Template nutzt Jinja2-Ausdruck für +1/-1 Jahr.
- **Files modified:** web/main/routes.py, web/templates/index.html
- **Commit:** e919aa1

## Known Stubs

Keine. Alle Kernfunktionen sind mit echten Daten verdrahtet:
- Jahr/Monat-Select: echte Werte aus Server-Zeit
- Org-Checkboxen: echte ORGANIZATIONS aus ENV
- result.html: echter formatted_text aus ChurchDesk-Konvertierung

## Self-Check

## Self-Check: PASSED

- web/templates/index.html: FOUND
- web/templates/result.html: FOUND
- web/main/routes.py: FOUND (upload_file entfernt, current_year hinzugefuegt)
- web/requirements.txt: FOUND (pandas/openpyxl entfernt)
- Commit 85639a8: FOUND
- Commit e919aa1: FOUND
- 95 Tests: PASSED
