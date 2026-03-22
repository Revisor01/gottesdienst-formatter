---
phase: quick
plan: 01
subsystem: location-extraction
tags: [location, formatting, churchdesk, boyens, tests]
dependency_graph:
  requires: []
  provides: [correct-location-extraction, kirche-suffix-removal, dash-separator-handling]
  affects: [web/churchdesk_api.py, web/formatting.py, web/tests/test_formatting.py]
tech_stack:
  added: []
  patterns: [parametrized-pytest, tdd-red-green]
key_files:
  created: []
  modified:
    - web/churchdesk_api.py
    - web/tests/test_formatting.py
decisions:
  - "Dash-Separator-Block vor 'No separator found' eingefuegt — Reihenfolge: pipe > comma > dash > multi-city-prefix > single-church-strip > LOCATION_MAPPINGS"
  - "Multi-city-Prefix-Pruefung mit location_lower.startswith(multi_city + ' ') statt startswith(multi_city + '-') unterscheidet Heide-Suederholm von Heide Erloeserkirche"
  - "format_service_type benoetigt keine Aenderung — 'abendmahl' in vollem Titel wird bereits korrekt erkannt, auch bei Kolon-Titeln"
metrics:
  duration: 8min
  completed: 2026-03-22
  tasks: 2
  files: 2
---

# Quick Task 260322-dpr: Fix Location Extraction — Remove Kirche Suffix

**One-liner:** extract_boyens_location erkennt Dash-Separator und Space-separated Ortsnamen und entfernt -Kirche-Suffix in Multi-Church-Staedten sowie trailing " Kirche" in Einzelkirchenorten.

## What Was Done

### Task 1 — RED: Fehlschlagende Tests

Import von `extract_boyens_location` in `test_formatting.py` hinzugefuegt und drei neue parametrisierte Testgruppen erstellt:

- `test_extract_boyens_location` (17 Cases): Heide Space-Patterns, Büsum Dash-Separator, Einzelkirchenorte, bestehende Pipe/Comma-Cases
- `test_extract_boyens_location_display` (3 Cases): Display-Modus Urlauberseelsorge vs. St. Clemens
- `test_format_service_type_sonderformat` (3 Cases): Kolon-Titel-Handling

12 Tests schlugen wie erwartet fehl. Die Sonderformat-Tests bestanden bereits — "abendmahl" im Kolon-Titel wird durch bestehende Logik korrekt erkannt.

Commit: `7107c35`

### Task 2 — GREEN: extract_boyens_location repariert

Zwei neue Verarbeitungsbloecke in `web/churchdesk_api.py` eingefuegt (nach Komma-Separator, vor LOCATION_MAPPINGS):

**Block 1 — Dash-Separator `' - '`:**
- "Büsum - St. Clemens-Kirche" → splitten, -Kirche entfernen, Büsum-Logik anwenden → "Büsum"
- "Büsum - Perlebucht" → "Büsum, Perlebucht"

**Block 2 — Multi-City-Prefix ohne Separator:**
- Prueft `location_lower.startswith(multi_city + ' ')` und NICHT `startswith(multi_city + '-')`
- "Heide St.-Jürgen-Kirche" → city="Heide", church="St.-Jürgen-Kirche" → strip -Kirche → "Heide, St.-Jürgen"
- "Heide Erlöserkirche" → "Heide, Erlöserkirche"
- "Heide-Süderholm" startet mit "heide-" → kein Match → unveraendert

**Block 3 — Single-Church trailing " Kirche":**
- "Hennstedt Kirche" → strip " Kirche" → "Hennstedt"
- Gleiches fuer Hemme, Lunden, Weddingstedt, Schlichting, St. Annen

Commit: `e668a72`

## Deviations from Plan

### Auto-fixed Issues

None.

### Planabweichung: format_service_type kein Fix noetig

**Found during:** Task 1 RED-Phase (Sonderformat-Tests bestanden sofort)

**Issue:** Plan beschrieb, dass "Gottesdienst mit Tisch-Abendmahl: Brot des Lebens" falsch behandelt werde. Tatsaechlich erkennt die bestehende `format_service_type`-Logik "abendmahl" auch im Kolon-Teil, da `titel_lower` den vollstaendigen Titel enthaelt.

**Fix:** Keine Aenderung an `web/formatting.py` vorgenommen — Plan-Artefakt `formatting.py` entfaellt.

**Commit:** Nicht benoetigt.

## Verification Results

- 66/66 Tests bestanden (inkl. Goldstandard und alle neuen Cases)
- `test_extract_boyens_location`: 17/17
- `test_extract_boyens_location_display`: 3/3
- `test_format_service_type_sonderformat`: 3/3
- Keine Regressions in bestehenden Tests

## Known Stubs

None.

## Self-Check: PASSED

- `/Users/simonluthe/Documents/kk-termine/web/churchdesk_api.py` — vorhanden und modifiziert
- `/Users/simonluthe/Documents/kk-termine/web/tests/test_formatting.py` — vorhanden und modifiziert
- Commit `7107c35` — vorhanden
- Commit `e668a72` — vorhanden
