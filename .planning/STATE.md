---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
stopped_at: "Checkpoint 03-02 Task 2: Server-Migration — wartet auf menschliche Verifikation"
last_updated: "2026-03-22T07:40:21.602Z"
progress:
  total_phases: 3
  completed_phases: 3
  total_plans: 7
  completed_plans: 7
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-21)

**Core value:** Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar
**Current focus:** Phase 03 — pipeline

## Current Position

Phase: 03 (pipeline) — EXECUTING
Plan: 2 of 2

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
| Phase 01-stabilisierung P01 | 132s | 3 tasks | 3 files |
| Phase 01-stabilisierung P02 | 196 | 2 tasks | 5 files |
| Phase 02-formatierung P01 | 96 | 2 tasks | 1 files |
| Phase 02-formatierung P02 | 10min | 2 tasks | 2 files |
| Phase 03-pipeline P01 | 173s | 2 tasks | 9 files |
| Phase 03-pipeline P02 | 3min | 1 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Brownfield-Stabilisierung vor Features: Code muss sauber sein bevor weitere APIs dazukommen
- Boyens-Fließtext als Referenzformat: Offizielle Vorgabe vom Chefredakteur, nicht verhandelbar
- [Phase 01-stabilisierung]: format_pastor basiert auf format_boyens_pastor-Logik (vollstaendig mit Delimiter-Splitting) statt simplem app.py-Fallback
- [Phase 01-stabilisierung]: ORGANIZATIONS-Dict ist leer wenn CHURCHDESK_ORG_IDS nicht gesetzt — kein Fallback auf hardcoded Tokens (SEC-01)
- [Phase 01-stabilisierung]: web/.env.example mit hardcoded Token aus Juli 2025 mitbereinigt (Rule 1 Auto-fix)
- [Phase 02-formatierung]: format_service_type Reihenfolge: spezifisch vor generisch (Konfirmandenprüfung vor Konfirmation, Abendmahl+Taufe vor Einzelchecks)
- [Phase 02-formatierung]: format_pastor Delimiter-Logik: erst & und und, dann Komma als Fallback; Diakon/Diakonin ausgeschrieben; Trennzeichen Komma statt &
- [Phase 02-formatierung]: jeweils-Logik nur bei identischem Pastor UND mehr als einem Eintrag am selben Ort
- [Phase 02-formatierung]: _build_location_entries() als geteilte Hilfsfunktion fuer Excel- und ChurchDesk-Pfad
- [Phase 02-formatierung]: Heide -Kirche Suffix entfernen; Brunsbüttel Kirchenname beibehalten (D-27)
- [Phase 03-pipeline]: pyproject.toml pythonpath=['.'] loest Import-Problem fuer pytest ohne sys.path-Hacks
- [Phase 03-pipeline]: Goldstandard-Fixture endet mit einfachem \n — entspricht join()-Output ohne doppelten Abschluss
- [Phase 03-pipeline]: Image-Name lowercase via IMAGE_LC erzwingen (Pitfall 4) — ghcr.io ist case-sensitive
- [Phase 03-pipeline]: Watchtower statt Portainer auf App-Server; ghcr.io Image auf public setzen damit kein Auth-Secret noetig

### Pending Todos

None yet.

### Blockers/Concerns

- API-Tokens sind im Git-History kompromittiert — müssen nach SEC-01 rotiert werden
- Büsum/Urlauberseelsorge-Mapping ist fragil (zuletzt zweimal gebrochen) — Tests in Phase 3 sind kritisch

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260322-dpr | Fix location extraction: remove Kirche suffix, fix separators, strip church names | 2026-03-22 | e668a72 | [260322-dpr](./quick/260322-dpr-fix-location-extraction-remove-kirche-su/) |

## Session Continuity

Last session: 2026-03-22
Stopped at: Completed quick task 260322-dpr: Location extraction fixes
Resume file: None
