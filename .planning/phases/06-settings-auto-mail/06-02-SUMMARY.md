---
phase: 06-settings-auto-mail
plan: 02
subsystem: ui
tags: [flask, wtforms, smtplib, fernet, blueprint, tailwind]

# Dependency graph
requires:
  - phase: 06-01
    provides: UserSettings DB-Modell und Fernet-Verschluesselungsmodul

provides:
  - Settings Blueprint mit GET/POST /settings und POST /settings/test-mail
  - SettingsForm mit allen SMTP-Feldern, send_day-Dropdown (1-28), auto_send_enabled
  - Tab-Layout-Template fuer Mail-Einstellungen und Organisations-Uebersicht
  - Sidebar-Link "Einstellungen" mit Zahnrad-Icon fuer alle eingeloggten User

affects:
  - 06-03 (Auto-Mail-Job baut auf UserSettings und SMTP-Logik aus routes.py auf)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Settings Blueprint Pattern analog zu admin/auth Blueprints
    - SMTP-Passwort nur bei Neueing abe verschluesseln, sonst bestehenden Wert behalten
    - Test-Mail via fetch() AJAX mit X-CSRFToken Header (kein csrftoken-Exempt)

key-files:
  created:
    - web/settings/__init__.py
    - web/settings/forms.py
    - web/settings/routes.py
    - web/templates/settings/settings.html
  modified:
    - web/app.py
    - web/templates/base.html

key-decisions:
  - "strict_slashes=False in Route-Dekorator statt Blueprint vermeidet 308-Redirect auf /settings/"
  - "Test-Mail-Funktion prueft alle Pflichtfelder vor SMTP-Versuch und gibt sprechende Fehlermeldungen zurueck"

patterns-established:
  - "Blueprint registrierung: from settings import bp as settings_bp / app.register_blueprint(settings_bp)"
  - "SMTP-Passwort-Handling: Leeres Formularfeld = nicht aendern (wie EditUserForm-Pattern)"
  - "AJAX CSRF: X-CSRFToken Header aus document.querySelector('input[name=csrf_token]').value"

requirements-completed: [SET-01, SET-03, SET-04]

# Metrics
duration: 15min
completed: 2026-03-22
---

# Phase 06 Plan 02: Settings-Blueprint Summary

**Flask Settings Blueprint mit Tab-Layout, SMTP-Formular mit Fernet-Verschluesselung, AJAX Test-Mail und Org-Uebersicht**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-22T13:00:00Z
- **Completed:** 2026-03-22T13:15:00Z
- **Tasks:** 2 (+ 1 Auto-fix Commit)
- **Files modified:** 6

## Accomplishments

- Settings Blueprint mit vollstaendigem CRUD fuer UserSettings (GET laedt Werte, POST speichert mit Fernet-Verschluesselung des SMTP-Passworts)
- POST /settings/test-mail sendet echte Test-Mail via smtplib (STARTTLS, Timeout 10s) und gibt JSON-Response zurueck
- Tab-Layout-Template mit Mail-Tab (alle SMTP-Felder, send_day-Dropdown, auto_send-Checkbox, Test-Mail-Button) und Org-Tab (readonly Cards)
- Sidebar-Link "Einstellungen" mit Zahnrad-Icon fuer alle eingeloggten User (nicht nur Admins)

## Task Commits

1. **Task 1: Settings Blueprint mit Forms und Routes** - `07889ca` (feat)
2. **Task 2: Settings-Template und Sidebar-Link** - `6960108` (feat)
3. **Auto-fix: strict_slashes Fix** - `c4c70af` (fix)

**Plan metadata:** wird nach SUMMARY committed

## Files Created/Modified

- `web/settings/__init__.py` - Blueprint-Definition (url_prefix='/settings')
- `web/settings/forms.py` - SettingsForm: SMTP-Felder, send_day SelectField 1-28, auto_send BooleanField, custom validate() fuer Pflichtfelder bei auto_send
- `web/settings/routes.py` - GET/POST /settings mit UserSettings CRUD + Fernet-Passwort, POST /settings/test-mail mit smtplib
- `web/templates/settings/settings.html` - Tab-Layout, Mail-Tab mit Formular und AJAX Test-Mail, Org-Tab readonly
- `web/app.py` - Settings Blueprint registriert
- `web/templates/base.html` - Einstellungen-Link mit Zahnrad-SVG fuer alle eingeloggten User

## Decisions Made

- `strict_slashes=False` in der Route-Dekorator (nicht im Blueprint-Konstruktor, der das Argument nicht unterstuetzt) vermeidet unnoetigen 308-Redirect beim Aufruf von `/settings` ohne Trailing Slash
- SMTP-Passwort-Handling: Leeres Passwortfeld beim Speichern = Bestehendes Passwort unveraendert lassen (analog zu EditUserForm-Pattern aus Phase 04)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 308-Redirect bei /settings ohne Trailing Slash**
- **Found during:** Task 1 Verifikation
- **Issue:** Blueprint mit `url_prefix='/settings'` und Route `'/'` erzeugte 308-Redirect von `/settings` zu `/settings/` wegen Flask-Default-Verhalten
- **Fix:** `strict_slashes=False` Parameter in `@bp.route('/', ...)` Dekorator hinzugefuegt
- **Files modified:** web/settings/routes.py
- **Verification:** `client.get('/settings')` liefert 302 (Login-Redirect), kein 308 mehr
- **Committed in:** c4c70af

---

**Total deviations:** 1 auto-fixed (Rule 1 Bug)
**Impact on plan:** Notwendige Korrektur fuer sauberes URL-Verhalten. Kein Scope Creep.

## Issues Encountered

Keine weiteren — Plan wie vorgesehen umgesetzt.

## Next Phase Readiness

- Plan 06-03 (Auto-Mail-Job) kann direkt auf UserSettings und SMTP-Logik aus routes.py aufbauen
- `test_mail()`-Funktion kann als Referenz fuer den automatischen Versand dienen
- APScheduler-Integration hat alle Voraussetzungen: UserSettings mit send_day, auto_send_enabled, smtp-Feldern

---
*Phase: 06-settings-auto-mail*
*Completed: 2026-03-22*
