---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: milestone
status: unknown
stopped_at: Completed 04-04-PLAN.md
last_updated: "2026-03-22T10:21:46.291Z"
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 11
  completed_plans: 11
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-22)

**Core value:** Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne redaktionelle Nacharbeit übernehmbar
**Current focus:** Phase 04 — fundament-auth

## Current Position

Phase: 04 (fundament-auth) — EXECUTING
Plan: 4 of 4

## Performance Metrics

**Velocity:**

- Total plans completed: 7
- Average duration: ~3 min
- Total execution time: ~21 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| Phase 01-stabilisierung P01 | 132s | 3 tasks | 3 files |
| Phase 01-stabilisierung P02 | 196s | 2 tasks | 5 files |
| Phase 02-formatierung P01 | 96s | 2 tasks | 1 files |
| Phase 02-formatierung P02 | 10min | 2 tasks | 2 files |
| Phase 03-pipeline P01 | 173s | 2 tasks | 9 files |
| Phase 03-pipeline P02 | 3min | 1 tasks | 2 files |

**Recent Trend:**

- Last 5 plans: ~3-10 min each
- Trend: Stabil

*Updated after each plan completion*
| Phase 04-fundament-auth P01 | 217 | 3 tasks | 13 files |
| Phase 04-fundament-auth P03 | 180 | 2 tasks | 3 files |
| Phase 04-fundament-auth P02 | 168 | 3 tasks | 11 files |
| Phase 04-fundament-auth P04 | 507 | 2 tasks | 8 files |

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
- [v2.0 Roadmap]: SQLite statt PostgreSQL — bewusste Entscheidung, reicht fuer <20 User
- [v2.0 Roadmap]: Flask-APScheduler in-process statt Celery/Redis — monatlicher Job, kein Overengineering
- [v2.0 Roadmap]: smtplib direkt statt Flask-Mail — Settings pro User aus DB, nicht global konfiguriert
- [v2.0 Roadmap]: Gunicorn Single-Worker-Constraint in docker-compose.yml — APScheduler darf nur einmal laufen
- [v2.0 Roadmap]: Tailwind CLI Build-Artefakt in static/css/ — kein Node.js im Docker-Container
- [Phase 04-fundament-auth]: extensions.py Singleton-Pattern ohne App-Binding — init_app() in create_app() loest Circular-Import-Problem
- [Phase 04-fundament-auth]: is_active_user als DB-Feld, is_active als Property — vermeidet Konflikt mit Flask-Login UserMixin
- [Phase 04-fundament-auth]: SECRET_KEY RuntimeError ohne Fallback — kein secrets.token_hex() als Sicherheitsnetz (Pitfall 1)
- [Phase 04-fundament-auth]: migrations/ im Repo committed — Container generiert keine Migrationen, nur flask db upgrade (Pitfall 2)
- [Phase 04-fundament-auth]: Auth Blueprint ohne url_prefix: /login direkt unter /, nicht /auth/login
- [Phase 04-fundament-auth]: POST-only Routes in Tests mit POST-Request (nicht GET, wuerde 405 liefern)
- [Phase 04-fundament-auth]: db.drop_all() + db.create_all() in Test-Setup: SQLAlchemy In-Memory SQLite teilt DB-State zwischen Tests
- [Phase 04-fundament-auth]: create_app(test_config) Parameter: Test-Konfiguration muss VOR db.init_app() gesetzt werden — SQLAlchemy cached Engine-URL beim init_app()
- [Phase 04-fundament-auth]: Flask-WTF formdata=None Problem: Leerer POST-Body (alle Checkboxen deaktiviert) wird als 'kein Formular' interpretiert — Submit-Button muss immer mitgesendet werden
- [Phase 04-fundament-auth]: admin_required als Decorator-Komposition aus login_required + is_admin Check — einfach und konsistent mit bestehendem Muster

### Critical Pitfalls for Phase 4

- SECRET_KEY muss persistent sein (nicht `secrets.token_hex` als Fallback) — Startup-Check mit RuntimeError
- Flask-Migrate von Anfang an, nie db.create_all() — `flask db upgrade` im Container-Entrypoint
- SQLite-Volume persistent in docker-compose.prod.yml mounten (`./data:/app/data`)
- Auth als atomare Änderung: alle Routes auf @login_required in einem Schritt, explizite Whitelist (/login, /health)

### Pending Todos

None.

### Blockers/Concerns

- API-Tokens sind im Git-History kompromittiert — müssen nach SEC-01 rotiert werden (aus v1.0 übertragen)
- Büsum/Urlauberseelsorge-Mapping ist fragil (zuletzt zweimal gebrochen) — Tests in Phase 3 sind kritisch

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260322-dpr | Fix location extraction: remove Kirche suffix, fix separators, strip church names | 2026-03-22 | e668a72 | [260322-dpr](./quick/260322-dpr-fix-location-extraction-remove-kirche-su/) |

## Session Continuity

Last session: 2026-03-22T10:21:46.289Z
Stopped at: Completed 04-04-PLAN.md
Resume file: None
Next action: `/gsd:plan-phase 4`
