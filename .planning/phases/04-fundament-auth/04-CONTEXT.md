# Phase 4: Fundament + Auth - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

App Factory Pattern, SQLite-Datenbank mit Flask-Migrate, Flask-Login mit Session-Auth, User-Verwaltung durch Admin, Health-Endpoint. Fundament für alle v2.0-Features.

</domain>

<decisions>
## Implementation Decisions

### Login-Erlebnis
- Einfaches zentriertes Login-Formular mit grünem Logo — minimal, funktional
- Session-Dauer: 30 Tage "Remember Me" — quasi dauerhaft eingeloggt
- Fehlgeschlagenes Login: Flash-Nachricht "Falscher Benutzername oder Passwort" — kein Lockout, kein Rate-Limiting
- Erster Admin-User via CLI-Befehl: `flask create-admin` — einmalig auf dem Server ausführen

### User-Verwaltung
- /admin Route mit eigenen Templates — schlicht, custom, kein Flask-Admin
- Keine Rollen — alle User sind gleich, nur ein is_admin Flag für User-Verwaltung
- Passwort: mindestens 8 Zeichen — kein Overkill für internes Tool
- User deaktivieren statt löschen — Audit-Trail bleibt erhalten

### Architektur (aus Research)
- App Factory Pattern: create_app() statt globaler Flask-Instanz
- Flask-SQLAlchemy + Flask-Migrate von Anfang an (nie db.create_all())
- SQLite mit Volume-Mount ./data:/app/data für Persistenz
- SECRET_KEY muss persistent sein — RuntimeError wenn nicht gesetzt (kein Fallback)
- CSRF-Schutz via Flask-WTF auf allen Formularen
- /health ohne Login erreichbar (Whitelist neben /login)

### Claude's Discretion
- Exakte DB-Schema-Struktur (User-Modell Felder)
- Blueprint-Organisation (auth, admin, main)
- Template-Vererbung / Base-Layout
- Entrypoint-Script für flask db upgrade

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bestehender Code
- `web/app.py` — Aktueller Zustand, muss auf App Factory umgebaut werden
- `web/config.py` — ENV-basierte Org-Konfiguration, bleibt erhalten
- `web/formatting.py` — Pure Functions, keine Änderung nötig
- `web/churchdesk_api.py` — API-Client, keine Änderung nötig
- `web/docker-compose.prod.yml` — Muss um SQLite-Volume und SECRET_KEY erweitert werden

### Research
- `.planning/research/ARCHITECTURE.md` — App Factory Pattern, Build-Order, Anti-Patterns
- `.planning/research/PITFALLS.md` — Kritische Pitfalls (SECRET_KEY, Migrationen, Volume)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- web/formatting.py — Pure Functions, kein Flask-Context nötig, bleibt unverändert
- web/config.py — ORGANIZATIONS Dict aus ENV, bleibt für ChurchDesk-Tokens
- web/templates/base.html — Basis-Template, wird in Phase 5 ersetzt (Tailwind)

### Established Patterns
- Route-Handler in app.py mit @app.route Dekoratoren
- Jinja2 Templates mit Template-Vererbung
- Flash-Messages für Benutzer-Feedback

### Integration Points
- app.py muss von globaler Instanz auf create_app() umgebaut werden
- Alle bestehenden Routes müssen @login_required bekommen
- docker-compose.prod.yml braucht SQLite Volume + SECRET_KEY ENV

</code_context>

<specifics>
## Specific Ideas

- Research empfiehlt: flask db upgrade im Container-Entrypoint (nicht in create_app())
- Werkzeug generate_password_hash / check_password_hash für Passwörter (bereits installiert)
- Gunicorn Single-Worker nicht in dieser Phase nötig (APScheduler kommt erst Phase 6)

</specifics>

<deferred>
## Deferred Ideas

- Tailwind CSS / UI Makeover → Phase 5
- Settings-Seite → Phase 6
- Auto-Mail → Phase 6

</deferred>

---

*Phase: 04-fundament-auth*
*Context gathered: 2026-03-22*
