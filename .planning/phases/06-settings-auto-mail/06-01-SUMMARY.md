---
phase: 06-settings-auto-mail
plan: "01"
subsystem: database
tags: [models, crypto, migration, fernet, sqlalchemy]
dependency_graph:
  requires: []
  provides: [UserSettings-model, crypto-module, user_settings-table]
  affects: [06-02-settings-blueprint, 06-03-auto-mail-scheduler]
tech_stack:
  added: [cryptography==42.0.5, APScheduler==3.10.4]
  patterns: [Fernet-encryption, PBKDF2-key-derivation, SQLAlchemy-model, Alembic-migration]
key_files:
  created:
    - web/crypto.py
    - web/migrations/versions/2c860eac220e_add_user_settings_table.py
  modified:
    - web/models.py
    - web/requirements.txt
decisions:
  - "Fernet-Key via PBKDF2HMAC aus SECRET_KEY abgeleitet — kein separater Schluessel noetig, deterministisch und sicher"
  - "Statischer Salt b'gottesdienst-formatter' — reicht fuer single-tenant Anwendungsfall"
  - "encrypt/decrypt nehmen secret_key als Parameter — kein flask.current_app in models.py, Verschluesselung in Routes"
metrics:
  duration_seconds: 70
  completed_date: "2026-03-22"
  tasks_completed: 2
  files_changed: 4
---

# Phase 06 Plan 01: UserSettings Model und Fernet-Verschluesselung Summary

**One-liner:** UserSettings SQLAlchemy-Modell mit 12 SMTP/Scheduling-Feldern und Fernet-Verschluesselung via PBKDF2-Ableitung aus SECRET_KEY.

## What Was Built

- **web/crypto.py**: Fernet-Verschluesselungsmodul mit `encrypt_value()` und `decrypt_value()`. Key-Ableitung via PBKDF2HMAC (SHA256, 480000 Iterationen, statischer Salt). Beide Funktionen nehmen `secret_key` als Parameter — kein Flask-Kontext im Modul noetig.
- **web/models.py**: `UserSettings`-Klasse (nach `User`) mit allen 12 Feldern gemaess CONTEXT.md-Schema. One-to-one Beziehung zu `User` via `backref('settings', uselist=False)`.
- **web/requirements.txt**: `cryptography==42.0.5` und `APScheduler==3.10.4` hinzugefuegt (APScheduler wird in Plan 03 aktiviert).
- **web/migrations/versions/2c860eac220e_add_user_settings_table.py**: Alembic-Migration erstellt `user_settings`-Tabelle mit FK `user_id -> users.id` (unique=True, nullable=False).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | crypto.py Fernet-Modul und UserSettings-Modell | 7246857 | web/crypto.py, web/models.py, web/requirements.txt |
| 2 | Alembic-Migration fuer UserSettings-Tabelle | 9e72775 | web/migrations/versions/2c860eac220e_add_user_settings_table.py |

## Verification Results

- `encrypt_value('test123', 'mysecret')` + `decrypt_value(enc, 'mysecret')` == `'test123'` — OK
- `UserSettings.__table__.columns` enthaelt alle 12 Felder — OK
- `flask db upgrade` erzeugt `user_settings`-Tabelle ohne Fehler — OK
- `PRAGMA table_info(user_settings)` bestaetigt 12 Spalten mit korrekten Namen — OK

## Deviations from Plan

Keine — Plan exakt wie geschrieben ausgefuehrt.

## Known Stubs

Keine — dieses Plan erstellt nur das Modell und die Migration, keine UI-Komponenten.

## Self-Check: PASSED

- [x] web/crypto.py existiert und importiert korrekt
- [x] web/models.py enthaelt UserSettings-Klasse
- [x] web/requirements.txt enthaelt cryptography und APScheduler
- [x] Migrationsdatei 2c860eac220e existiert in web/migrations/versions/
- [x] Commits 7246857 und 9e72775 vorhanden
