---
phase: 03-pipeline
plan: 02
subsystem: infra
tags: [github-actions, docker, ghcr.io, watchtower, ci-cd]

requires:
  - phase: 03-01
    provides: pytest-Infrastruktur und Tests als CI-Gate

provides:
  - GitHub Actions CI/CD-Workflow (test + build-and-push)
  - docker-compose.prod.yml mit Watchtower fuer Auto-Deploy
  - Vollautomatische Pipeline: git push -> Tests -> Image -> ghcr.io -> Watchtower

affects: [deployment, server-migration]

tech-stack:
  added: [github-actions, docker/build-push-action@v6, docker/login-action@v3, docker/metadata-action@v5, containrrr/watchtower]
  patterns: [image-from-registry-not-build, watchtower-auto-deploy, lowercase-image-name-env]

key-files:
  created:
    - .github/workflows/ci-cd.yml
    - web/docker-compose.prod.yml
  modified: []

key-decisions:
  - "Image-Name lowercase via IMAGE_LC erzwingen (Pitfall 4 aus RESEARCH) — ghcr.io ist case-sensitive"
  - "docker-compose.prod.yml ohne version:'3.8' (deprecated in Compose V2)"
  - "Watchtower pollt alle 300s; ghcr.io Image auf public setzen damit kein Auth-Secret in Watchtower noetig"
  - "requirements.txt UND requirements-dev.txt werden in CI installiert (pandas fuer Tests benoetigt)"

patterns-established:
  - "CI/CD: test-Job als Gate vor build-and-push mit needs: test"
  - "Prod-Compose nutzt image: von ghcr.io statt build: . (kein Quellcode auf Server)"
  - "Watchtower als Auto-Deploy ohne Portainer auf App-Server"

requirements-completed: [DEPLOY-01, DEPLOY-02, DEPLOY-03]

duration: 3min
completed: 2026-03-22
---

# Phase 3 Plan 2: CI/CD-Pipeline und Produktions-Compose Summary

**GitHub Actions CI/CD-Pipeline mit ghcr.io-Push und Watchtower-Auto-Deploy: git push auf main triggert Tests, baut Docker-Image und deployed es automatisch auf den Server**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T07:39:00Z
- **Completed:** 2026-03-22T07:42:00Z
- **Tasks:** 1/2 (Task 2 ist Checkpoint — wartet auf menschliche Verifikation)
- **Files modified:** 2

## Accomplishments

- GitHub Actions Workflow mit test-Job (pytest als Gate) und build-and-push-Job (ghcr.io)
- Produktions-Compose mit image: statt build: und Watchtower-Service (5-Minuten-Poll)
- Image-Name lowercase via `IMAGE_LC=${GITHUB_REPOSITORY,,}` (Pitfall 4 aus RESEARCH vermieden)
- Alle ENV-Vars aus bestehender docker-compose.yml uebernommen; kein version:'3.8' (Compose V2)

## Task Commits

1. **Task 1: GitHub Actions CI/CD-Workflow und Produktions-Compose erstellen** - `893aa16` (feat)
2. **Task 2: Server-Migration pruefen und ghcr.io-Paket freischalten** - _Checkpoint: wartet auf Verifikation_

## Files Created/Modified

- `.github/workflows/ci-cd.yml` - CI/CD-Workflow mit test- und build-and-push-Jobs
- `web/docker-compose.prod.yml` - Produktions-Compose mit ghcr.io-Image und Watchtower

## Decisions Made

- Image-Name lowercase via `IMAGE_LC=${GITHUB_REPOSITORY,,}` erzwungen — ghcr.io verlangt lowercase, GitHub-Repo kann Grossbuchstaben haben
- `requirements.txt` UND `requirements-dev.txt` werden in CI installiert, da pandas fuer Formatierungs-Tests benoetigt wird
- Kein `version: '3.8'` in docker-compose.prod.yml (deprecated/ignored in Compose V2)
- Watchtower mit `WATCHTOWER_POLL_INTERVAL=300` (5 Minuten) — ausreichend fuer Nutzungsfrequenz

## Deviations from Plan

Keine — Plan exakt wie beschrieben umgesetzt.

## User Setup Required

**Task 2 erfordert manuelle Schritte (Checkpoint):**

1. GitHub Actions pruefen: https://github.com/Revisor01/gottesdienst-formatter/actions
2. ghcr.io-Package auf "Public" setzen: https://github.com/users/Revisor01/packages/container/gottesdienst-formatter/settings
3. Server einmalig umstellen:
   ```bash
   ssh root@185.248.143.234
   cd /opt/gottesdienst-formatter/web
   cp docker-compose.yml docker-compose.yml.bak
   cp docker-compose.prod.yml docker-compose.yml
   # .env pruefen/aktualisieren
   docker compose pull && docker compose up -d
   docker ps  # gottesdienst-formatter und watchtower-gd muessen laufen
   ```
4. Funktionstest: http://gd.kkd-fahrtenbuch.de

## Next Phase Readiness

Nach Abschluss von Task 2 (Server-Migration):
- Vollautomatische Pipeline aktiv: git push -> Tests -> Image -> Auto-Deploy
- Kein manueller SSH-Zugriff fuer Deployments mehr noetig
- Phase 3 abgeschlossen

---
*Phase: 03-pipeline*
*Completed: 2026-03-22*
