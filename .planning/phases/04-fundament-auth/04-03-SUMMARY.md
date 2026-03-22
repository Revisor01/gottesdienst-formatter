---
phase: 04-fundament-auth
plan: 03
subsystem: docker
tags: [docker, sqlite, gunicorn, migrations, entrypoint]
dependency_graph:
  requires: [04-01]
  provides: [FOUND-03]
  affects: [docker-deployment, database-persistence]
tech_stack:
  added: [gunicorn]
  patterns: [entrypoint-script, docker-volume-mount, flask-db-upgrade-on-start]
key_files:
  created:
    - web/entrypoint.sh
  modified:
    - web/Dockerfile
    - web/docker-compose.prod.yml
decisions:
  - "entrypoint.sh fuehrt flask db upgrade vor Gunicorn-Start aus — Migrationen laufen automatisch bei jedem Container-Start"
  - "Single Worker in Gunicorn — Vorbereitung fuer APScheduler in Phase 6 (kein Multi-Worker-Problem)"
  - "Gunicorn statt python app.py — Produktionstauglicher WSGI-Server"
metrics:
  duration_seconds: 180
  completed_date: "2026-03-22"
  tasks_completed: 2
  files_changed: 3
---

# Phase 04 Plan 03: Docker-Konfiguration fuer persistente SQLite-Datenbank Summary

**One-liner:** Docker-Produktionskonfiguration mit persistentem SQLite-Volume, automatischer Migration via entrypoint.sh und Gunicorn als Single-Worker WSGI-Server.

## What Was Built

- `web/entrypoint.sh`: Shell-Script das beim Container-Start `flask db upgrade` ausfuehrt und dann Gunicorn startet
- `web/Dockerfile`: Aktualisiert mit ENTRYPOINT statt CMD, `/app/data` Verzeichnis, HEALTHCHECK und chmod fuer entrypoint.sh
- `web/docker-compose.prod.yml`: SQLite-Volume `./data:/app/data` und `FLASK_APP=app:create_app()` hinzugefuegt

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Entrypoint-Script und Dockerfile | b578e4a | web/entrypoint.sh, web/Dockerfile |
| 2 | docker-compose.prod.yml mit SQLite Volume | c77b9de | web/docker-compose.prod.yml |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- web/entrypoint.sh: FOUND
- web/Dockerfile: FOUND (HEALTHCHECK + ENTRYPOINT)
- web/docker-compose.prod.yml: FOUND (./data:/app/data + FLASK_APP)
- Commit b578e4a: FOUND
- Commit c77b9de: FOUND
