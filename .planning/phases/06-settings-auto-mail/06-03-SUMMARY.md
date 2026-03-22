---
phase: 06-settings-auto-mail
plan: "03"
subsystem: scheduler
tags: [apscheduler, mail, automation, smtp, cron]
dependency_graph:
  requires: ["06-02"]
  provides: [auto-mail-scheduler, mail-service]
  affects: [web/app.py]
tech_stack:
  added: [APScheduler 3.10.4 (BackgroundScheduler + CronTrigger)]
  patterns: [atexit cleanup, app_context injection, cron-daily-job, retry-via-date-job]
key_files:
  created:
    - web/mail_service.py
    - web/scheduler.py
  modified:
    - web/app.py
decisions:
  - "generate_next_month_export() nutzt lokalen Import von convert_churchdesk_events_to_boyens um Circular-Import zu vermeiden"
  - "atexit-Handler ignoriert SchedulerNotRunningError — tritt auf wenn Scheduler manuell vor Prozessende gestoppt wird (Tests)"
  - "check_and_send_mails() prueft last_send_date im selben Jahr+Monat als Deduplizierung"
metrics:
  duration: 128s
  completed: "2026-03-22T12:58:31Z"
  tasks_completed: 2
  files_created: 2
  files_modified: 1
---

# Phase 06 Plan 03: APScheduler Mail-Versand Summary

**One-liner:** APScheduler mit täglichem 08:00-Cron-Job für automatischen Boyens-Export-Versand inkl. Sa/So→Freitag-Logik und 1h-Retry.

## What Was Built

Zwei neue Module und eine App-Integration:

1. **web/mail_service.py** — Versandlogik und Export-Generierung
2. **web/scheduler.py** — APScheduler-Setup mit täglichem Check-Job
3. **web/app.py** — `init_scheduler(app)` nach Blueprint-Registrierung

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Mail-Service (Versandlogik und Export-Generierung) | 0affde3 | web/mail_service.py |
| 2 | APScheduler-Setup und Integration in create_app() | ee6fc7f | web/scheduler.py, web/app.py |

## Key Implementation Details

### mail_service.py

**`get_effective_send_date(year, month, day)`**
- Samstag (weekday 5) → -1 Tag (Freitag)
- Sonntag (weekday 6) → -2 Tage (Freitag)
- Begrenzt day auf letzten Monatstag (Sicherheitsnetz)

**`generate_next_month_export()`**
- Dezember → Januar nächstes Jahr (Jahresübergang)
- Alle ORGANIZATIONS via create_multi_org_client
- Lokaler Import von convert_churchdesk_events_to_boyens (Circular-Import-Vermeidung)
- Leerer String bei leeren Events (kein Fehler)

**`send_boyens_mail(user_settings, export_text, secret_key)`**
- MIMEMultipart('mixed') mit Body + Anhang (gleicher Text)
- Dateiname: gottesdienste_{monat}_{jahr}.txt
- smtplib mit starttls(), timeout=30
- Exception-Handling: SMTPAuthenticationError, SMTPException, socket.timeout

### scheduler.py

**`init_scheduler(app)`**
- TESTING-Guard: kein Start im Test-Modus
- Werkzeug-Reloader-Guard: nur starten wenn WERKZEUG_RUN_MAIN != 'false'
- CronTrigger(hour=8, minute=0) mit misfire_grace_time=3600
- app._scheduler = scheduler für Job-Zugriff
- atexit-Handler mit Fehler-Unterdrückung

**`check_and_send_mails(app)`**
- Lädt alle UserSettings mit auto_send_enabled=True und smtp_server gesetzt
- Pro User: effective_date berechnen, bei Match: Deduplizierung prüfen, Export generieren, Mail senden
- Bei Fehler: Retry-Job nach 1h einplanen (date-based APScheduler job)
- Exception-Handling pro User mit db.session.rollback()

**`retry_send_mail(app, settings_id, export_text)`**
- Einmaliger Retry-Job
- last_send_date wird auch bei Fehler gesetzt (markiert als "versucht")
- Status: "Fehlgeschlagen nach Retry: ..." bei erneutem Fehler

## Deviations from Plan

### Auto-fixed Issues

None — Plan executed exactly as written.

### Minor Adjustments

**1. atexit Exception-Handling**
- **Found during:** Task 2 Verifikation
- **Issue:** Lambda `lambda: scheduler.shutdown(wait=False)` warf `SchedulerNotRunningError` in Tests wenn Scheduler manuell gestoppt wurde
- **Fix:** Named function mit try/except statt Lambda
- **Files modified:** web/scheduler.py

## Known Stubs

None — alle implementierten Funktionen sind vollständig verdrahtet.

## Self-Check: PASSED

- [x] web/mail_service.py existiert
- [x] web/scheduler.py existiert
- [x] web/app.py enthält init_scheduler
- [x] Commits 0affde3 und ee6fc7f existieren
- [x] Weekend-Logik-Tests bestanden
- [x] App-Import-Tests bestanden
