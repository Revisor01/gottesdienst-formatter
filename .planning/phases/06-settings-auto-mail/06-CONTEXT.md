# Phase 6: Settings + Auto-Mail - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Settings-Seite für Mail-Konfiguration pro User, Org-Übersicht, automatischer monatlicher E-Mail-Versand des Boyens-Exports. Letzte Phase von v2.0.

</domain>

<decisions>
## Implementation Decisions

### Settings-Seite
- Tab-Layout: "Mail-Einstellungen" / "Organisationen"
- SMTP-Konfiguration pro User: Server, Port, Absender, Empfänger, Passwort
- SMTP-Passwort Fernet-verschlüsselt mit APP_SECRET (cryptography-Lib) — NICHT Klartext
- Test-Mail-Button: Sendet Test-Mail an die konfigurierte Empfänger-Adresse
- Organisationen-Tab: Readonly Card mit Name + Description aus ENV — User kann nichts ändern, nur sehen welche Orgs aktiv sind
- Versand-Tag: Dropdown 1-28 (Default: 18)

### Auto-Mail
- Nächster Monat wird automatisch generiert — am 18. März wird April-Export verschickt
- Versand um 8:00 Uhr morgens am gewählten Tag
- **Wochenend-Logik**: Wenn Versand-Tag auf Sa/So fällt, auf den Freitag davor vorziehen
- Retry 1x nach 1 Stunde bei fehlgeschlagenem Versand, dann Flash-Warnung beim nächsten Login
- Mail enthält formatierten Text als .txt-Anhang UND im Mail-Body
- APScheduler in-process, Single-Worker-Constraint (Gunicorn --workers 1)
- smtplib direkt (nicht Flask-Mail) — weil SMTP-Settings pro User aus DB

### Datenbank-Schema (UserSettings)
- user_id (FK zu User)
- smtp_server, smtp_port (default 587), smtp_username, smtp_password_encrypted
- sender_email, recipient_email
- send_day (int 1-28, default 18)
- auto_send_enabled (bool, default False)
- last_send_date, last_send_status

### Claude's Discretion
- Exakte Fernet-Implementierung (Key-Derivation aus SECRET_KEY)
- APScheduler Job-Konfiguration
- Template-Design für Settings-Seite (Tailwind, passend zum grünen Theme)
- Error-Handling bei SMTP-Fehlern (Timeout, Auth-Fehler, etc.)

</decisions>

<canonical_refs>
## Canonical References

### Bestehender Code
- `web/app.py` — create_app() Factory, Blueprint-Registrierung
- `web/models.py` — User-Modell, hier UserSettings-Modell ergänzen
- `web/extensions.py` — db, migrate, login_manager
- `web/main/routes.py` — convert_churchdesk_events_to_boyens() für Export-Generierung
- `web/churchdesk_api.py` — create_multi_org_client() für API-Zugriff
- `web/config.py` — ORGANIZATIONS Dict (readonly für Settings-Anzeige)

### Research
- `.planning/research/ARCHITECTURE.md` — smtplib statt Flask-Mail, APScheduler Pattern
- `.planning/research/PITFALLS.md` — Single-Worker-Constraint, Scheduler-Pitfalls

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- convert_churchdesk_events_to_boyens() — generiert den Export-Text, kann für Mail wiederverwendet werden
- create_multi_org_client() — API-Client für Event-Abruf
- ORGANIZATIONS Dict aus config.py — für Org-Übersicht in Settings

### Established Patterns
- Blueprint-Organisation (main, auth, admin) — Settings als neuer Blueprint
- Flask-WTF Forms mit CSRF
- Tailwind-Klassen für UI (card, btn-primary, input-field)
- Flask-Migrate für DB-Änderungen

### Integration Points
- UserSettings-Modell in models.py hinzufügen
- Settings-Blueprint in app.py registrieren
- APScheduler in create_app() initialisieren
- Sidebar-Link zu Settings in base.html
- Migration für neue UserSettings-Tabelle

</code_context>

<specifics>
## Specific Ideas

- Settings-Link in der Sidebar mit Zahnrad-Icon
- Test-Mail-Button: "Test senden" → Spinner → "Erfolgreich" / "Fehler: ..."
- Org-Cards zeigen: Name, Description, Anzahl Events im aktuellen Monat (optional)
- Versand-Logik: get_next_send_date(day=18) → prüft Wochentag, zieht auf Freitag vor wenn nötig

</specifics>

<deferred>
## Deferred Ideas

- ChurchDesk-Org-Verwaltung in Settings statt ENV → v3 Feature
- Diff-Ansicht zwischen Exporten → v3 Feature
- Dark Mode → nicht geplant

</deferred>

---

*Phase: 06-settings-auto-mail*
*Context gathered: 2026-03-22*
