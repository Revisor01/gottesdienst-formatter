---
phase: 04-fundament-auth
plan: "04"
subsystem: auth
tags: [flask, admin, user-management, cli, wtforms, sqlalchemy]

# Dependency graph
requires:
  - phase: 04-02
    provides: User-Model, Auth-Blueprint, login_required auf allen Routes
  - phase: 04-03
    provides: CSRF-Schutz via Flask-WTF

provides:
  - Admin-Blueprint mit /admin/users, /admin/users/new, /admin/users/<id>/edit
  - admin_required Decorator (login_required + is_admin Check)
  - flask create-admin CLI-Befehl fuer ersten Admin-User
  - CreateUserForm, EditUserForm mit Validierung
  - Admin-Link in Navbar (nur fuer is_admin-User sichtbar)
  - 6 Test-Cases fuer Admin-Zugriffskontrolle und CRUD
  - create_app(test_config) Parameter fuer korrekte Test-Isolation

affects: [05-scheduler, 06-email, zukuenftige Phasen mit User-bezogenen Features]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - admin_required Decorator als Komposition aus login_required + is_admin Check
    - create_app(test_config) Factory-Pattern fuer Test-Config vor db.init_app()
    - StaticPool + Submit-Button in Tests fuer korrekte WTForms-Formular-Verarbeitung

key-files:
  created:
    - web/admin/__init__.py
    - web/admin/routes.py
    - web/admin/forms.py
    - web/templates/admin/users.html
    - web/templates/admin/edit_user.html
    - web/tests/test_admin.py
  modified:
    - web/app.py
    - web/templates/base.html

key-decisions:
  - "create_app(test_config) Parameter: Test-Konfiguration muss VOR db.init_app() gesetzt werden — SQLAlchemy cached Engine-URL beim ersten init_app()"
  - "Flask-WTF formdata=None Problem: Leerer POST-Body (nur deaktivierte Checkboxen) wird als 'kein Formular' interpretiert — Submit-Button muss immer mitgesendet werden"
  - "admin_required als Decorator-Komposition statt Klassen-Decorator — einfacher und konsistent mit bestehendem login_required Muster"

patterns-established:
  - "Admin-Zugriffskontrolle: @admin_required Decorator auf allen /admin/* Routes"
  - "Test-App-Factory: create_app(test_config={...}) mit StaticPool fuer zuverlässige In-Memory Tests"
  - "Formular-Test-Pattern: Submit-Button-Wert muss in Test-POST-Data enthalten sein"

requirements-completed: [AUTH-04]

# Metrics
duration: 8min
completed: 2026-03-22
---

# Phase 04 Plan 04: Admin User-Management Summary

**Admin-CRUD via /admin/users mit flask create-admin CLI, admin_required Decorator und 6 Integrations-Tests**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-22T10:12:01Z
- **Completed:** 2026-03-22T10:20:28Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Admin kann User anlegen, bearbeiten (Passwort-Reset) und deaktivieren (nicht loeschen)
- flask create-admin CLI erstellt ersten Admin-User ohne DB-Zugriff
- Nicht-Admins bekommen 403 auf allen /admin/* Routes, Anonyme bekommen Redirect auf /login
- Admin-Link in Navbar nur fuer is_admin-User sichtbar

## Task Commits

Jeder Task wurde atomar committed:

1. **Task 1: Admin Blueprint mit User-CRUD** - `5f51ec3` (feat)
2. **Task 2: CLI, Blueprint-Registrierung, Admin-Link, Tests** - `110b2c6` (feat)

**Plan-Metadaten:** folgt (docs-Commit)

## Files Created/Modified
- `web/admin/__init__.py` - Blueprint-Definition mit url_prefix='/admin'
- `web/admin/routes.py` - admin_required Decorator, /users, /users/new, /users/<id>/edit
- `web/admin/forms.py` - CreateUserForm (username+passwort+is_admin), EditUserForm (passwort+is_admin+is_active)
- `web/templates/admin/users.html` - User-Liste mit Bootstrap-Tabelle
- `web/templates/admin/edit_user.html` - Formular fuer neu/bearbeiten (is_new Flag)
- `web/app.py` - test_config Parameter, Admin-Blueprint, flask create-admin CLI
- `web/templates/base.html` - Admin-Link in Navbar ({% if current_user.is_admin %})
- `web/tests/test_admin.py` - 6 Tests: Zugriffskontrolle (3), CRUD (2), CLI (1)

## Decisions Made

- `create_app(test_config)`: Test-Konfiguration muss VOR `db.init_app()` gesetzt werden. SQLAlchemy cached die Engine-URL beim `init_app()`-Aufruf, daher ist ein nachträgliches Setzen von `SQLALCHEMY_DATABASE_URI` wirkungslos.
- Flask-WTF interpretiert einen leeren POST-Body (z.B. alle Checkboxen deaktiviert) als "kein Formular eingereicht" und gibt `formdata=None` zurück. WTForms füllt dann das Formular aus dem `obj=user` Parameter — das ergibt falsche (pre-filled) Werte. Lösung: Submit-Button muss im POST-Body enthalten sein.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Flask-WTF formdata=None bei leerem POST-Body**
- **Found during:** Task 2 (test_admin_can_deactivate_user Test)
- **Issue:** `EditUserForm(obj=user)` bei POST ohne Body-Inhalt: Flask-WTF gibt `formdata=None` zurück wenn `request.form` leer ist, dadurch befüllt WTForms das Formular aus `obj=user` statt aus Request-Daten. is_active_user blieb `True` obwohl es auf `False` gesetzt werden sollte.
- **Fix:** (1) `create_app(test_config)` Parameter hinzugefügt damit SQLAlchemy die Engine mit korrekter Test-Config erstellt. (2) Test sendet `data={'submit': 'Speichern'}` damit `request.form` nicht leer ist. (3) StaticPool für konsistente In-Memory DB-Verbindungen.
- **Files modified:** `web/app.py`, `web/tests/test_admin.py`
- **Verification:** `python -m pytest web/tests/test_admin.py -v` → 6 passed
- **Committed in:** `110b2c6` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — Bug in Test-Setup und WTForms-Formular-Verarbeitung)
**Impact on plan:** Auto-fix notwendig fuer Korrektheit. Test deckt reales Browser-Verhalten korrekt ab (Browser sendet immer Submit-Button). Kein Scope Creep.

## Issues Encountered

- SQLAlchemy Engine-URL-Caching: Nachträgliches Setzen von `SQLALCHEMY_DATABASE_URI` nach `create_app()` ohne `test_config` Parameter hat keine Wirkung — Engine ist bereits mit der Original-URI erstellt. Drei Debugging-Runden bis zur Ursache. Lösung: Factory-Pattern mit `test_config`.
- Flask-WTF `formdata=None` Verhalten: Nicht offensichtlich aus der Dokumentation. Leerer POST-Body != "alle Felder False". Submit-Button-Wert als Marker notwendig.

## User Setup Required

Keiner fuer diesen Plan — aber vor Produktion muss ein Admin-User via CLI erstellt werden:
```bash
SECRET_KEY=<key> flask create-admin <username>
```

## Next Phase Readiness

- Vollständige Auth-Infrastruktur komplett: Login, Logout, User-Modell, Admin-CRUD, CLI
- Phase 04 (fundament-auth) ist damit vollständig abgeschlossen
- Nächste Phase (05 oder folgende) kann User-Verwaltung und is_admin-Flag nutzen

---
*Phase: 04-fundament-auth*
*Completed: 2026-03-22*
