---
phase: 03-pipeline
plan: 01
subsystem: testing
tags: [pytest, unit-tests, goldstandard, formatting, tdd]
dependency_graph:
  requires: []
  provides: [test-infrastructure, formatting-tests, goldstandard-fixture]
  affects: [web/formatting.py]
tech_stack:
  added: [pytest>=8.0]
  patterns: [parametrize, conftest, pyproject.toml pythonpath]
key_files:
  created:
    - web/requirements-dev.txt
    - web/pyproject.toml
    - web/tests/__init__.py
    - web/tests/conftest.py
    - web/tests/test_formatting.py
    - web/tests/fixtures/boyens_reference_input.json
    - web/tests/fixtures/boyens_reference_output.txt
    - web/tests/test_boyens_goldstandard.py
  modified:
    - web/formatting.py
decisions:
  - "pyproject.toml pythonpath=['.'] loest Import-Problem ohne sys.path-Hacks in Tests"
  - "Goldstandard-Fixture prueft Zeilenumbruch-Verhalten: Output endet mit \\n (kein doppelter Abschluss)"
  - "[Rule 1 Auto-fix] 'tauf' statt 'taufe' in format_service_type — deckt Taufgottesdienst ab"
metrics:
  duration: "173s"
  completed: "2026-03-22"
  tasks: 2
  files: 9
---

# Phase 03 Plan 01: pytest-Infrastruktur und Goldstandard-Tests Summary

**One-liner:** pytest-Testsuite mit 44 parametrisierten Unit-Tests und Goldstandard-End-to-End-Fixture fuer alle Boyens-Formatierungsfunktionen.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | pytest-Infrastruktur und Unit-Tests fuer formatting.py | 3821c82 | requirements-dev.txt, pyproject.toml, tests/__init__.py, conftest.py, test_formatting.py |
| 2 | Goldstandard-Fixture und End-to-End-Formatierungstest | f51a98d | fixtures/boyens_reference_input.json, fixtures/boyens_reference_output.txt, test_boyens_goldstandard.py |

## What Was Built

### Task 1: pytest-Infrastruktur

- `web/requirements-dev.txt`: Test-Dependencies (pytest>=8.0, pandas, openpyxl)
- `web/pyproject.toml`: pytest konfiguriert mit `pythonpath = ["."]` und `testpaths = ["tests"]`
- `web/tests/conftest.py`: sys.path-Fix als Backup fuer pyproject.toml
- `web/tests/test_formatting.py`: 42 parametrisierte Tests fuer alle 4 Funktionen:
  - `format_date`: 8 Tests (7 parametrisiert + NaT)
  - `format_time`: 8 Tests (7 parametrisiert + NaT)
  - `format_service_type`: 17 Tests (14 parametrisiert + NaT + 2 case-insensitive)
  - `format_pastor`: 10 Tests (parametrisiert inkl. Sonderzeichen & Team, Diakon/in)

### Task 2: Goldstandard-Fixture

- `boyens_reference_input.json`: 4 statische Events an 2 Tagen (Sonntag 6. April und 13. April 2025)
- `boyens_reference_output.txt`: Exakter erwarteter Boyens-Fliesstext
- `test_boyens_goldstandard.py`: 2 Tests:
  - Gesamtvergleich (exact string match)
  - Zeilenweiser Vergleich fuer bessere Fehlermeldungen

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] format_service_type: 'Taufgottesdienst' wurde nicht erkannt**
- **Found during:** Task 1, RED-Phase
- **Issue:** `'taufe' in 'taufgottesdienst'` ist False — "taufgottesdienst" enthaelt "tauf" + "gottesdienst", das Wort "taufe" kommt nicht vor
- **Fix:** Prüfung auf `'tauf' in titel_lower` statt `'taufe' in titel_lower` (Zeilen 77 und 81 in formatting.py). "Tauffest" wird weiterhin korrekt abgefangen, weil der Check dafuer frueher steht.
- **Files modified:** web/formatting.py
- **Commit:** 3821c82

**2. [Rule 3 - Blocking] Goldstandard-Fixture: abschliessender Zeilenumbruch**
- **Found during:** Task 2, GREEN-Phase
- **Issue:** Fixture-Datei hatte doppelten abschliessenden Zeilenumbruch (`\n\n`), tatsaechlicher Output endet mit einfachem `\n`
- **Fix:** boyens_reference_output.txt auf korrekten einzeiligen Abschluss angepasst
- **Files modified:** web/tests/fixtures/boyens_reference_output.txt

## Test Results

```
44 passed in 0.42s
```

- test_formatting.py: 42 Tests gruen
- test_boyens_goldstandard.py: 2 Tests gruen

## Self-Check: PASSED
