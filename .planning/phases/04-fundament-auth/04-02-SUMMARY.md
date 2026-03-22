---
phase: 04-fundament-auth
plan: 02
subsystem: auth
tags: [flask-login, flask-wtf, csrf, login, logout, login_required]

requires:
  - phase: 04-fundament-auth plan 01
    provides: extensions.py Singletons (LoginManager, CSRFProtect), User-Modell, App-Factory

provides:
  - Auth Blueprint mit /login und /logout Routes
  - LoginForm mit CSRF via hidden_tag()
  - @login_required auf allen 5 main-Routes
  - /health Whitelist ohne Login-Anforderung
  - Login-Template (zentriert, minimal)
  - CSRF-Tokens in allen bestehenden HTML-Forms
  - Logout-Link in Navbar wenn eingeloggt
  - 12 Auth-Tests (TestProtectedRoutes + TestLogin)

affects:
  - 04-03 (admin blueprint baut auf auth auf)
  - 04-04 (settings nutzt login_required und current_user)

tech-stack:
  added: []
  patterns:
    - "@login_required Decorator auf Route-Ebene (nicht Blueprint-Ebene)"
    - "Auth Blueprint ohne url_prefix — /login direkt unter /"
    - "CSRF via form.hidden_tag() fuer WTF-Forms, csrf_token() fuer HTML-Forms"
    - "Flash-Messages mit Kategorien (danger/info/warning) in base.html"
    - "db.drop_all() + db.create_all() in Test-Setup fuer saubere Test-Isolation"

key-files:
  created:
    - web/auth/__init__.py
    - web/auth/routes.py
    - web/auth/forms.py
    - web/templates/auth/login.html
    - web/tests/test_auth.py
  modified:
    - web/main/routes.py
    - web/app.py
    - web/templates/base.html
    - web/templates/index.html
    - web/templates/result.html
    - web/templates/churchdesk_events.html
    - web/tests/test_app_factory.py

key-decisions:
  - "Auth Blueprint ohne url_prefix: /login liegt direkt unter /, nicht /auth/login"
  - "Admin-Link in Navbar wird erst in Plan 04 hinzugefuegt, nicht vorab"
  - "POST-only Routes in Tests mit POST-Requests testen (nicht GET, wuerde 405 liefern)"
  - "db.drop_all() + db.create_all() pro Test-Klasse: SQLAlchemy In-Memory SQLite teilt DB-State"

patterns-established:
  - "Route-Schutz: @bp.route(...) → @login_required → def func (Reihenfolge beachten)"
  - "CSRF in WTF-Forms: form.hidden_tag() in Template"
  - "CSRF in HTML-Forms: <input type='hidden' name='csrf_token' value='{{ csrf_token() }}'/>"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-05, FOUND-05]

duration: 3min
completed: 2026-03-22
---

# Phase 04 Plan 02: Auth-System Summary

**Flask-Login Auth mit /login, /logout, @login_required auf allen Routes, CSRF-Schutz und /health Whitelist**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T10:07:12Z
- **Completed:** 2026-03-22T10:10:00Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Auth Blueprint mit Login/Logout-Routes und LoginForm (Flask-WTF, CSRF automatisch)
- Alle 5 bestehenden main-Routes mit @login_required geschuetzt, /health ohne Login erreichbar
- 12 Auth-Tests bestehen: Redirect-auf-Login, Login-Erfolg, falsches Passwort, Logout, deaktivierter User

## Task Commits

1. **Task 1: Auth Blueprint mit Login/Logout und CSRF-Forms** - `ffb950b` (feat)
2. **Task 2: @login_required auf alle Routes + /health + Blueprint-Registrierung + base.html** - `5a50008` (feat)
3. **Task 3: Auth-Tests** - `3692237` (test)

## Files Created/Modified

- `web/auth/__init__.py` - Auth Blueprint ohne url_prefix
- `web/auth/routes.py` - /login (GET/POST) und /logout Routes
- `web/auth/forms.py` - LoginForm mit Flask-WTF (CSRF automatisch via hidden_tag)
- `web/templates/auth/login.html` - Zentriertes Login-Formular mit form.hidden_tag()
- `web/main/routes.py` - @login_required auf index, upload, download, fetch, export; /health ohne Auth
- `web/app.py` - Auth Blueprint registriert
- `web/templates/base.html` - Navbar mit Username und Abmelden-Link; Flash-Message-Kategorien
- `web/templates/index.html` - CSRF-Token in ChurchDesk-Fetch-Form und Excel-Upload-Form
- `web/templates/result.html` - CSRF-Token in Download-Form
- `web/templates/churchdesk_events.html` - CSRF-Token in Export-Form
- `web/tests/test_auth.py` - 12 Auth-Tests (TestProtectedRoutes + TestLogin)
- `web/tests/test_app_factory.py` - test_index_route_exists auf neues Redirect-Verhalten aktualisiert

## Decisions Made

- Auth Blueprint ohne url_prefix: /login liegt direkt unter /, nicht /auth/login — konsistenter mit Erwartungen
- POST-only Routes muessen in Tests mit POST getestet werden (GET liefert 405, nicht 302)
- db.drop_all() + db.create_all() pro Test-Klasse noetig, da SQLAlchemy In-Memory SQLite DB-State zwischen Tests teilt
- Admin-Link in Navbar erst in Plan 04 (admin Blueprint) — vorab wuerde er ins Leere zeigen

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_index_route_exists erwartet 200 statt 302**
- **Found during:** Task 2 (nach @login_required auf alle Routes)
- **Issue:** Bestehender Test erwartet HTTP 200 fuer /, aber Route leitet jetzt ohne Login auf /login um (302)
- **Fix:** Test umbenannt und auf neue Erwartung (302 + Location /login) aktualisiert
- **Files modified:** web/tests/test_app_factory.py
- **Verification:** 84 Tests bestehen nach Fix
- **Committed in:** 5a50008 (Task 2 commit)

**2. [Rule 1 - Bug] TestProtectedRoutes.test_redirect_to_login schickt GET an POST-only Routes**
- **Found during:** Task 3 (beim ersten Test-Run)
- **Issue:** /upload, /download etc. sind POST-only Routes — GET liefert 405 statt 302
- **Fix:** Parametrisierung auf (path, method) Tupel umgestellt; POST-Routes mit POST-Request getestet
- **Files modified:** web/tests/test_auth.py
- **Verification:** Alle 12 Tests bestehen
- **Committed in:** 3692237 (Task 3 commit)

**3. [Rule 1 - Bug] UNIQUE constraint failed in TestLogin wegen geteiltem DB-State**
- **Found during:** Task 3 (beim zweiten Test-Run)
- **Issue:** SQLAlchemy In-Memory SQLite teilt DB zwischen Test-Klassen; create_test_user versucht 'testuser' erneut einzufuegen
- **Fix:** db.drop_all() vor db.create_all() in create_test_app() hinzugefuegt
- **Files modified:** web/tests/test_auth.py
- **Verification:** Alle 12 Tests bestehen in beliebiger Reihenfolge
- **Committed in:** 3692237 (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (alle Rule 1 - Bugs)
**Impact on plan:** Alle Auto-Fixes notwendig fuer Korrektheit. Kein Scope-Creep.

## Issues Encountered

Keine ausserplanmaessigen Blocker.

## Next Phase Readiness

- Auth-System vollstaendig: Login, Logout, @login_required, CSRF, /health
- Admin Blueprint (Plan 03) kann jetzt current_user und is_admin nutzen
- Settings Blueprint (Plan 04) kann current_user.id fuer user-spezifische Settings nutzen

---
*Phase: 04-fundament-auth*
*Completed: 2026-03-22*
