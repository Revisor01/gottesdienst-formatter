---
phase: 04-fundament-auth
plan: 01
subsystem: web
tags: [flask, app-factory, sqlalchemy, flask-migrate, flask-login, blueprint, auth-foundation]
dependency_graph:
  requires: []
  provides: [app-factory, user-model, db-migrations, main-blueprint]
  affects: [web/app.py, web/extensions.py, web/models.py, web/main/]
tech_stack:
  added: [Flask-SQLAlchemy==3.1.1, Flask-Migrate==4.0.7, Flask-Login==0.6.3, Flask-WTF==1.2.2, gunicorn==21.2.0]
  patterns: [app-factory, blueprint-pattern, alembic-migrations]
key_files:
  created:
    - web/extensions.py
    - web/models.py
    - web/main/__init__.py
    - web/main/routes.py
    - web/migrations/
    - web/tests/test_app_factory.py
  modified:
    - web/app.py
    - web/requirements.txt
    - web/templates/base.html
    - web/templates/index.html
    - web/templates/result.html
    - web/templates/churchdesk_events.html
    - web/tests/test_boyens_goldstandard.py
decisions:
  - "extensions.py als Singleton-Modul ohne App-Binding — init_app() in create_app() loest Circular-Import-Problem"
  - "is_active_user als DB-Feld, is_active als Property — vermeidet Konflikt mit Flask-Login UserMixin"
  - "SECRET_KEY RuntimeError ohne Fallback — Pitfall 1 aus Phase-4-Kontext explizit umgesetzt"
  - "migrations/ im Repo committed — Pitfall 2, Container generiert keine Migrationen"
metrics:
  duration: 217s
  completed: 2026-03-22
  tasks: 3
  files: 13
requirements: [FOUND-01, FOUND-02, FOUND-04]
---

# Phase 4 Plan 1: App Factory und Fundament Summary

Flask-App von globalem `app`-Objekt auf App Factory Pattern (create_app()) umgebaut mit SQLAlchemy/Flask-Migrate, User-Modell, Main-Blueprint und SECRET_KEY RuntimeError-Check.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Extensions, Models und requirements.txt | 0fe85a2 | web/extensions.py, web/models.py, web/requirements.txt |
| 2 | App Factory und Main Blueprint | c0dc24a | web/app.py, web/main/, web/migrations/, web/templates/ |
| 3 | Tests und Smoke-Verify | 1d85296 | web/tests/test_app_factory.py, web/tests/test_boyens_goldstandard.py |

## Verification Results

1. `flask routes` zeigt alle 5 Routes unter main-Blueprint: OK
2. `flask db upgrade` laeuft fehlerfrei: OK
3. `python -m pytest tests/` — 72 Tests gruen (6 neue + 66 bestehende): OK
4. `SECRET_KEY='' create_app()` — RuntimeError ausgeloest: OK

## Decisions Made

- **extensions.py Singleton-Pattern**: db, migrate, login_manager, csrf werden ohne App-Binding deklariert, init_app() erst in create_app(). Verhindert Circular Imports.
- **is_active_user als DB-Feld**: Die Flask-Login UserMixin-Property `is_active` wird als Property ueberschrieben, die auf `is_active_user` zeigt. Trennt DB-Spalte von Interface-Methode.
- **SECRET_KEY RuntimeError**: Kein Fallback auf `secrets.token_hex()`. App startet nicht ohne gesetzten Key. Pitfall 1 aus der Phase-4-Analyse explizit abgesichert.
- **migrations/ im Repo**: Alembic-Ordner committed. Container fuehrt nur `flask db upgrade` aus, generiert keine Migrationen. Pitfall 2 abgesichert.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Import-Fix in bestehenden Goldstandard-Tests**
- **Found during:** Task 3
- **Issue:** `test_boyens_goldstandard.py` importierte `_build_location_entries` und `_extract_suffix` direkt aus `app`. Nach dem Refactor liegen diese Funktionen in `main.routes`.
- **Fix:** Import auf `from main.routes import _build_location_entries, _extract_suffix` aktualisiert
- **Files modified:** web/tests/test_boyens_goldstandard.py
- **Commit:** 1d85296

## Known Stubs

None — alle bestehenden Funktionen wurden vollstaendig in den Blueprint migriert. Keine Platzhalter oder leere Implementierungen.

## Self-Check: PASSED

All 7 key files exist. All 3 task commits verified in git history.
