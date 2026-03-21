---
phase: 02-formatierung
plan: 02
subsystem: output-assembly
tags: [output, location, sorting, grouping, boyens]
dependency_graph:
  requires: ["02-01"]
  provides: ["boyens-output-assembly", "multi-church-locations"]
  affects: ["web/app.py", "web/churchdesk_api.py"]
tech_stack:
  added: []
  patterns: ["location-dict-grouping", "jeweils-logic", "suffix-extraction"]
key_files:
  created: []
  modified:
    - web/app.py
    - web/churchdesk_api.py
decisions:
  - "jeweils-Logik nur bei identischem Pastor UND mehr als einem Eintrag am selben Ort"
  - "_build_location_entries() als geteilte Hilfsfunktion fuer Excel- und ChurchDesk-Pfad"
  - "Heide Komma-Format: -Kirche Suffix entfernen; Brunsbüttel: Kirchenname immer beibehalten"
metrics:
  duration: "~10min"
  completed: "2026-03-21"
  tasks: 2
  files_changed: 2
---

# Phase 02 Plan 02: Output-Assembly und Location-Extraktion Summary

**One-liner:** Boyens-konformer Fließtext-Output mit alphabetischer Ort-Sortierung, Semikolon-Multi-Termin, jeweils-Logik und korrekten Multi-Church-Städtenamen.

## What Was Built

### Task 1: Multi-Church-Locations in churchdesk_api.py (commit ae9a90c)

`extract_boyens_location()` korrigiert:

- **Heide (Komma- und Pipe-Format):** `-Kirche` Suffix wird entfernt → `"Heide, St.-Jürgen-Kirche"` → `"Heide, St.-Jürgen"` (D-27)
- **Brunsbüttel:** Kirchenname wird beibehalten statt auf Stadtname reduziert → `"Brunsbüttel, Jakobuskirche"` bleibt (D-27)
- **Büsum im Komma-Format:** St. Clemens → `"Büsum"` (nicht `"Büsum, St. Clemens"`) (D-28)
- Pipe-Format und Komma-Format identisch behandelt

### Task 2: Output-Assembly in app.py (commit 0c74926)

Neue Hilfsfunktionen:

- `_extract_suffix(titel)` — extrahiert `", anschl. Kirchcafé"` aus Titeln (D-12)
- `_build_location_entries(day_items)` — gemeinsame Logik für alphabetische Sortierung (D-29), Semikolon-Zusammenfassung (D-31) und jeweils-Logik (D-20/FMT-08)

Überarbeitung beider Output-Pfade:

- `process_excel_file()`: Verwendet jetzt `extract_boyens_location()` für Location-Extraktion aus Excel-Daten; nutzt `_build_location_entries()`
- `convert_churchdesk_events_to_boyens()`: Ebenfalls auf `_build_location_entries()` umgestellt

**Beispiel-Output:**
```
Sonnabend, 5. April:
Albersdorf: 11 Uhr, Gd. m. A.; 15.30 Uhr, Kinderkirche, jeweils Pn. Schmidt
Brunsbüttel, Jakobuskirche: 10 Uhr, Gd., P. Soost
Büsum: 9 Uhr, Gd., Pn. Luthe
Heide, St.-Jürgen: 17 Uhr, Gd., Pn. Christ
Meldorf: 9.30 Uhr, Gd., P. Müller
```

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| jeweils nur bei >1 Eintrag mit identischem Pastor | Einzeltermin braucht kein jeweils |
| _build_location_entries() als geteilte Hilfsfunktion | DRY: Excel- und ChurchDesk-Pfad teilen selbe Logik |
| Brunsbüttel immer mit Kirchenname | D-27: Brunsbüttel hat mehrere Kirchen |

## Deviations from Plan

None — Plan executed exactly as written.

## Known Stubs

None — alle Location-Extraktionen und Output-Pfade sind korrekt verdrahtet.

## Self-Check: PASSED

- web/app.py modified: FOUND
- web/churchdesk_api.py modified: FOUND
- Task 1 commit ae9a90c: FOUND
- Task 2 commit 0c74926: FOUND
- All assertions in verify scripts: PASSED
