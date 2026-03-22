---
phase: quick
plan: 260322-kaw
subsystem: web
tags: [organizations, database, admin, config, migration]
tech-stack:
  added: []
  patterns: [SQLite single-source-of-truth, module-level cache with reload]
key-files:
  created:
    - web/migrations/versions/e4f63c8b0c96_add_organizations_table.py
    - web/templates/admin/organizations.html
    - web/templates/admin/edit_organization.html
  modified:
    - web/models.py
    - web/config.py
    - web/app.py
    - web/admin/routes.py
    - web/admin/forms.py
    - web/templates/settings/settings.html
    - web/templates/base.html
    - web/docker-compose.prod.yml
decisions:
  - Load orgs into module-level ORGANIZATIONS dict at app startup; call reload_organizations() after admin CRUD to keep in-process cache fresh
  - Organization primary key = ChurchDesk org ID (integer, not auto-increment) for direct lookup compatibility
  - Tokens stored plain text in SQLite (not encrypted) per task spec
metrics:
  duration: ~20min
  completed: 2026-03-22
  tasks: 6 commits
  files: 8 modified, 3 created
---

# Quick Task 260322-kaw: Organisationen im Web-Interface statt ENV-Vars

**One-liner:** SQLite-Tabelle `organizations` ersetzt alle `CHURCHDESK_ORG_*` Env-Vars als Single Source of Truth, mit Admin-CRUD-Interface im Web.

## Was wurde gemacht

### 1. Organization Model (models.py)
Neues `Organization` DB-Modell mit Feldern: `id` (ChurchDesk Org-ID als PK), `name`, `token`, `description`, `is_active`.

### 2. Alembic Migration mit Seed-Daten
Migration `e4f63c8b0c96_add_organizations_table.py` erstellt die Tabelle und befüllt sie mit 4 Organisationen:
- 2596: Kirchenkreis Dithmarschen
- 6572: Kirchspiel Heide
- 2725: Kirchspiel Eider
- 2729: Kirchspiel West

### 3. config.py komplett neu geschrieben
- `load_organizations()` fragt jetzt `Organization.query.filter_by(is_active=True)` ab
- `reload_organizations()` aktualisiert das modul-level `ORGANIZATIONS`-Dict nach Admin-Änderungen
- Kein ENV-Var-Code mehr

### 4. app.py: Startup-Load
`reload_organizations()` wird in `create_app()` innerhalb des App-Kontexts aufgerufen, sodass `ORGANIZATIONS` beim ersten Request befüllt ist.

### 5. Admin-CRUD (admin/routes.py + admin/forms.py)
- `OrganizationForm` mit allen Feldern
- `GET /admin/organizations` — Übersichtstabelle
- `GET/POST /admin/organizations/new` — Anlegen
- `GET/POST /admin/organizations/<id>/edit` — Bearbeiten
- `POST /admin/organizations/<id>/delete` — Löschen mit JS-Bestätigung
- Alle Routen `@admin_required`; nach jedem Write `_reload_orgs()` aufgerufen

### 6. Templates
- `admin/organizations.html`: Tabelle mit ID, Name, Beschreibung, Status, Edit/Delete
- `admin/edit_organization.html`: Formular für Anlegen/Bearbeiten

### 7. Settings Org-Tab
Readonly-Text entfernt; Admin-Button "Organisationen verwalten" → `/admin/organizations` hinzugefügt.

### 8. Sidebar (base.html)
"Organisationen"-Link für Admins unterhalb von "Benutzer" eingefügt.

### 9. docker-compose.prod.yml
Alle `CHURCHDESK_ORG_*` Env-Vars entfernt. Verbleiben: `SECRET_KEY`, `FLASK_ENV`, `FLASK_DEBUG`, `FLASK_APP`.

### 10. churchdesk_api.py
Keine Änderung nötig — `create_multi_org_client()` und `MultiOrganizationChurchDeskAPI` verwenden bereits `from config import ORGANIZATIONS`, das jetzt DB-backed ist.

## Commits

| Hash | Beschreibung |
|------|-------------|
| 3d95b70 | feat: add Organization model and migration with seed data |
| 9482681 | feat: load organizations from DB instead of env vars |
| 7e0705a | feat: add admin CRUD routes and forms for organizations |
| 31407a7 | feat: add admin templates for organization management |
| 73acc16 | feat: update settings org-tab and sidebar for org management |
| 6413af0 | chore: remove CHURCHDESK_ORG_* env vars from docker-compose.prod.yml |

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - all data is live from DB.

## Deployment-Hinweis

Beim nächsten Deploy auf dem Server muss `flask db upgrade` ausgeführt werden, damit die `organizations`-Tabelle angelegt und mit den 4 Seed-Orgs befüllt wird. Die `.env`-Datei auf dem Server kann danach um alle `CHURCHDESK_ORG_*` Variablen bereinigt werden.

```bash
ssh root@185.248.143.234 "cd /opt/gottesdienst-formatter && git pull origin main && cd web && docker compose -f docker-compose.prod.yml run --rm gottesdienst-formatter flask db upgrade && docker compose -f docker-compose.prod.yml up -d"
```

## Self-Check: PASSED

- web/models.py: Organization class vorhanden
- web/migrations/versions/e4f63c8b0c96_add_organizations_table.py: existiert
- web/config.py: reload_organizations() implementiert
- web/templates/admin/organizations.html: existiert
- web/templates/admin/edit_organization.html: existiert
- App-Start-Test: 4 Organisationen aus DB geladen (IDs: 2596, 2725, 2729, 6572)
- Route-Test: alle 4 Admin-Routen auflösbar
