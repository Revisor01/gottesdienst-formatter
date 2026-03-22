# Project Research Summary

**Project:** Gottesdienst-Formatter v2.0
**Domain:** Flask Web App — Authentication, User Settings, Auto-Email, UI Overhaul
**Researched:** 2026-03-22
**Confidence:** HIGH

## Executive Summary

Der Gottesdienst-Formatter ist ein internes Werkzeug fuer den Kirchenkreis Dithmarschen, das ChurchDesk-Ereignisse in das Boyens-Medien-Druckformat konvertiert. Version 2.0 verwandelt das bisherige Single-User-Skript in eine echte Multi-User-Webanwendung mit Authentifizierung, persistenten Nutzereinstellungen und automatischem E-Mail-Versand. Das Flask-Oekosystem bietet alle benoetigen Bausteine als reife, gut dokumentierte Erweiterungen: Flask-Login fuer Session-Management, Flask-SQLAlchemy mit SQLite fuer Persistenz, smtplib fuer dynamischen SMTP-Versand pro Nutzer, Flask-APScheduler fuer monatlichen automatischen Versand und Tailwind CSS CLI fuer das UI-Makeover. Der bestehende Kern (formatting.py, churchdesk_api.py) bleibt unveraendert.

Der empfohlene Ansatz strukturiert die Implementierung in vier abhaengigkeitsgesteuerte Phasen: Zuerst das Fundament (App Factory, Datenbank, Authentication), dann UI-Makeover, danach Nutzereinstellungen und Mail-Versand, und schliesslich den automatischen Scheduler. Dieses Vorgehen entspricht exakt der Build-Order aus der Architekturforschung und stellt sicher, dass jede Phase auf einem verifizierten Fundament aufbaut. Die gesamte App bleibt schlank: SQLite statt PostgreSQL, Flask-APScheduler statt Celery/Redis, smtplib statt globalem Flask-Mail — bewusste Entscheidungen gegen Over-Engineering.

Die kritischsten Risiken liegen saemtlich in Phase 1 und muessen dort adressiert werden: persistenter SECRET_KEY (sonst Session-Verlust bei jedem Deploy), Flask-Migrate statt db.create_all() (sonst Datenverlust bei Schema-Aenderungen), SQLite-Volume-Mount in docker-compose.yml (sonst Datenverlust bei Watchtower-Redeployment) und atomare Auth-Abdeckung aller Routes (keine halbgare Absicherung). Werden diese vier Punkte in Phase 1 korrekt umgesetzt, sind alle spaeteren Phasen technisch risikoarm.

## Key Findings

### Recommended Stack

Der bestehende Stack (Flask 2.3.3, pandas, requests, openpyxl, Werkzeug, pytz) bleibt unveraendert. Hinzu kommen ausschliesslich bewaehrte Pallets-Ecosystem-Erweiterungen. Werkzeug ist bereits installiert und liefert sicheres Passwort-Hashing ohne zusaetzliche Abhaengigkeit. SQLite in einem Docker-Volume ist die korrekte Datenbank-Wahl fuer eine interne App mit maximal 20 Nutzern — kein PostgreSQL-Overhead noetig. Tailwind CSS wird ueber einen lokalen Build-Schritt in ein statisches CSS-File kompiliert, das im Docker-Image landet — kein Node.js im Container.

**Core technologies:**
- Flask-Login 0.6.3: Session-Management, @login_required — Standard fuer Flask-Auth, Pallets Ecosystem
- Flask-SQLAlchemy 3.1.1: ORM fuer User-Modell und Settings — offizielle Flask-Erweiterung
- Flask-Migrate 4.1.0: Schema-Migrationen via Alembic — v4.0+ automatisch SQLite-kompatibel (batch-mode)
- Flask-WTF 1.2.2: CSRF-Schutz fuer alle POST-Formulare — Pallets Ecosystem, Oktober 2024
- smtplib (stdlib): Dynamischer SMTP-Versand pro User aus DB-Settings — keine Extra-Dependency
- Flask-APScheduler: Monatlicher Mail-Versand in-process — kein Celery/Redis noetig
- Tailwind CSS CLI v4.x: Build-Artefakt in static/css/, kein Node.js im Container

**Was nicht verwendet werden soll:**
- Flask-Bcrypt (nicht aktiv gewartet seit 2022) — Werkzeug.security stattdessen
- Tailwind Play CDN in Produktion — explizit "not for production" laut offizieller Doku
- Celery + Redis — Overengineering fuer einen monatlichen Job
- Flask-Security-Too — 10x mehr Features als noetig
- PostgreSQL — kein Mehrwert bei weniger als 20 Nutzern

### Expected Features

**Must have (v2.0 Launch):**
- Login / Logout / @login_required auf allen Routes — Multi-User-Schutz
- Passwort-Hashing mit Werkzeug — Basis-Sicherheit
- Datenbank-Setup (SQLAlchemy + SQLite, User-Modell) — Fundament fuer alles
- CSRF-Schutz (Flask-WTF) — Sicherheits-Baseline
- Settings-Seite pro User (SMTP, Empfaenger-Mail) — Voraussetzung fuer Auto-Mail
- Auto-E-Mail an Boyens (per Knopf aus Result-Seite) — Kernmehrwert v2.0
- Admin-Panel User-Verwaltung (anlegen, Passwort setzen, is_admin) — Betrieb ohne Server-Zugriff
- Excel-Import entfernen — UI-Bereinigung
- UI-Makeover (gruen) — gesetzte Anforderung
- Health-Check Endpoint /health — Docker + Uptime-Kuma

**Sollte ergaenzt werden nach v2.0-Launch (v2.x):**
- Vorschau mit Warnungen vor dem Senden — erhoehtes Vertrauen in Output
- Sonderformat-Titel-Parsing-Erweiterung — Qualitaetsverbesserung
- Passwort-Aenderung durch User selbst — Komfort-Feature

**Zurueckstellen (v3+):**
- E-Mail-Versandhistorie
- Mehrere Empfaenger pro User
- Vorlagen-Verwaltung fuer Sonderformate

**Anti-Features (bewusst nicht bauen):**
- OAuth/SSO — unverhealtnismaessige Komplexitaet fuer < 20 interne User
- Passwort-Reset per E-Mail — Henne-Ei-Problem (SMTP muss funktionieren bevor User einloggt)
- 2FA — unverhealtnismaessig fuer internes Tool
- Flask-Admin Integration — generische CRUD-Views passen nicht zum Custom-Workflow

### Architecture Approach

Die Architektur folgt dem App-Factory-Pattern mit drei Blueprints (auth, main, settings) und einer zentralen extensions.py, die zirkulaere Imports verhindert. Der bestehende Monolith (app.py) wird in diese Struktur refaktoriert — main/ nimmt die bereits existierenden Routes auf, auth/ und settings/ sind neu. Der Scheduler laeuft in-process als Flask-APScheduler mit explizitem Single-Worker-Constraint. Mail-Versand erfolgt per smtplib direkt aus UserSettings-Objekten, nicht ueber global konfiguriertes Flask-Mail.

**Major components:**
1. extensions.py — db, login_manager, scheduler instanziiert aber erst in create_app() gebunden (init_app Pattern)
2. models.py — User (id, username, password_hash, is_admin) + UserSettings (SMTP-Config, Org-IDs, auto_send_day)
3. auth/routes.py — /login, /logout, /admin/users mit @admin_required
4. main/routes.py — alle bestehenden Formatter-Routes, jetzt mit @login_required
5. settings/routes.py — /settings/mail, /settings/orgs, CRUD gegen UserSettings
6. mail_service.py — smtplib-basierter Versand aus UserSettings-Objekt, Fernet-Verschluesselung fuer smtp_pass
7. scheduler.py — APScheduler CronJob taeglich 08:00, iteriert ueber User mit mail_enabled=True

**Build Order (nicht aenderbar — Abhaengigkeiten erzwingen diese Reihenfolge):**
1. App Factory + extensions.py
2. SQLAlchemy Models + Flask-Migrate
3. Flask-Login + auth Blueprint
4. @login_required auf alle main/ Routes
5. Settings Blueprint + UserSettings CRUD
6. mail_service.py (smtplib)
7. APScheduler + monatlicher Job
8. Admin User-Verwaltung

### Critical Pitfalls

1. **SECRET_KEY ohne persistenten Wert** — Startup-Check `if not os.getenv('SECRET_KEY'): raise RuntimeError(...)`, Key einmalig generieren und dauerhaft in .env auf Server hinterlegen; kein `secrets.token_hex(32)` als Fallback in Produktion

2. **db.create_all() statt Flask-Migrate** — Flask-Migrate von Anfang an, `flask db upgrade` im Container-Entrypoint; Migrations-Ordner ins Git-Repo commiten; SQLite-Volume persistent mounten (`./data:/app/data`)

3. **Unvollstaendige Auth-Abdeckung** — Auth als atomare Aenderung: in einem Schritt alle Routes auf @login_required umstellen; explizite Whitelist fuer oeffentliche Routes (nur /login, /health); nach Einbau mit `curl` ohne Cookie testen

4. **APScheduler mit mehreren Worker-Prozessen** — Gunicorn explizit auf 1 Worker beschraenken in docker-compose.yml; bei Multi-Worker wird die monatliche Mail mehrfach versendet

5. **UI-Makeover bricht JavaScript** — vor Beginn alle JS-abhaengigen Element-IDs dokumentieren (#events-form, #formatted-output, [name="selected_events"]); nach Makeover manuell End-to-End testen (ChurchDesk → Auswahl → Export → Clipboard)

## Implications for Roadmap

Basierend auf der Forschung (insbesondere der Build-Order aus ARCHITECTURE.md und dem Pitfall-to-Phase-Mapping aus PITFALLS.md) ergibt sich folgende Phasenstruktur:

### Phase 1: Datenbank und Auth Foundation

**Rationale:** Alle anderen Features haengen von Datenbank und Authentication ab. Kein anderes Feature kann gebaut werden bevor User-Modell, Login und @login_required existieren. Alle kritischen Deployment-Pitfalls (SECRET_KEY, Volume, Migrationen) muessen hier geloest werden — nicht spaeter.

**Delivers:** Funktionierendes Multi-User-Login, persistente Datenbank ueber Deploys hinweg, alle bestehenden Routes hinter Auth, App-Factory-Struktur mit Blueprints

**Addresses features from FEATURES.md:**
- Login / Logout / @login_required
- Passwort-Hashing (Werkzeug)
- Datenbank-Setup (SQLAlchemy + SQLite)
- CSRF-Schutz (Flask-WTF)
- Health-Check /health
- Excel-Import entfernen (isoliert, keine Abhaengigkeit — hier erledigen)

**Must avoid (from PITFALLS.md):**
- SECRET_KEY Fallback (Pitfall 1)
- db.create_all() statt Flask-Migrate (Pitfall 2)
- Ungeschuetzte Routes nach Auth-Integration (Pitfall 3)
- SQLite-Datei im Container ohne Volume (Pitfall 4)

### Phase 2: UI Makeover

**Rationale:** Das UI-Makeover ist funktional unabhaengig von Settings und Mail (laut FEATURES.md Feature-Dependencies). Es sollte vor Settings/Mail kommen, weil Settings-Templates mit dem neuen UI-System gebaut werden koennen — kein doppeltes Styling. Tailwind-Build-Setup hier einrichten, damit alle folgenden Templates sofort das neue System nutzen.

**Delivers:** Gruene Farbpalette, Tailwind-CSS-Build-Pipeline, aktualisierte base.html mit Login-State-Navigation, alle existierenden Templates im neuen Design

**Addresses features from FEATURES.md:**
- UI-Makeover (gruen)

**Uses from STACK.md:**
- Tailwind CSS CLI v4.x (npm-Build lokal, output.css im Repo)

**Must avoid (from PITFALLS.md):**
- JS-Abhaengigkeiten in Templates zerstoeren (Pitfall 7): Vor Beginn JS-Element-IDs dokumentieren, nach Abschluss End-to-End-Test

### Phase 3: User Settings und Auto-Mail

**Rationale:** Settings und Mail sind eng gekoppelt (SMTP-Config ist Voraussetzung fuer Mail-Versand). Sie bilden zusammen den Kernmehrwert von v2.0. Die Phase setzt Phase 1 (User-Modell in DB) voraus. smtplib direkt statt Flask-Mail verwenden, da Settings pro User dynamisch geladen werden muessen.

**Delivers:** Settings-Seite pro User (SMTP, Empfaenger-Mail, Org-Auswahl), "Mail an Boyens senden"-Button in Result-Seite, Admin-Panel fuer User-Verwaltung, Fernet-Verschluesselung fuer SMTP-Passwort

**Addresses features from FEATURES.md:**
- Settings-Seite pro User
- Auto-E-Mail an Boyens
- Admin-Panel User-Verwaltung

**Uses from STACK.md:**
- smtplib (stdlib) — kein Flask-Mail fuer dynamische Settings
- Fernet (cryptography) — Verschluesselung smtp_pass

**Must avoid (from PITFALLS.md):**
- Flask-Mail global konfigurieren (Anti-Pattern 1 in ARCHITECTURE.md)
- Fehlende Startup-Validierung wenn SMTP nicht konfiguriert (Pitfall 6)

### Phase 4: Automatischer Monatlicher E-Mail-Versand

**Rationale:** Der Scheduler setzt alles aus den Phasen 1-3 voraus: User-Modell, Settings, mail_service.py. Er ist funktional isoliert und kann zum Schluss gebaut werden ohne andere Features zu blockieren.

**Delivers:** APScheduler CronJob (taeglich 08:00), monatlicher automatischer Versand fuer User mit mail_enabled=True und konfiguriertem auto_send_day, expliziter Single-Worker-Constraint in docker-compose.yml

**Addresses features from FEATURES.md:**
- (Implizit durch Auto-Mail-Feature — Scheduler ist technische Infrastruktur dafuer)

**Uses from STACK.md:**
- Flask-APScheduler (in-process, kein Celery/Redis)

**Must avoid (from PITFALLS.md):**
- APScheduler mit mehreren Worker-Prozessen (Pitfall 5)
- App-Context fehlt im Task-Body (Integration Gotcha in PITFALLS.md)
- Lautloser Fehler bei fehlendem SMTP (Pitfall 6)

### Phase Ordering Rationale

- **Auth vor allem anderen:** Feature-Dependency-Graph aus FEATURES.md zeigt, dass Datenbank und Login der Wurzelknoten sind. Nichts anderes ist ohne sie aufbaubar.
- **UI vor Settings/Mail:** Settings-Templates koennen direkt im neuen Tailwind-System gebaut werden — vermeidet doppeltes Styling-Refactoring. Das UI ist funktional unabhaengig (explizit so dokumentiert in FEATURES.md).
- **Settings/Mail gemeinsam:** Beide sind eng gekoppelt (SMTP-Config ist Voraussetzung fuer Mail-Versand). Getrennt bauen wuerde eine nicht funktionsfaehige Zwischenstufe erzeugen.
- **Scheduler zuletzt:** Setzt alle anderen Phasen voraus. Kann isoliert zum Ende gebaut werden.

### Research Flags

Phasen die voraussichtlich kein weiteres Research benoetigen (etablierte Patterns):
- **Phase 1 (DB + Auth):** Exzellent dokumentiert — Flask-Login, Flask-SQLAlchemy, Flask-Migrate sind Pallets-Standard. Pitfalls vollstaendig identifiziert.
- **Phase 2 (UI):** Tailwind CSS CLI ist straightforward. Einziges Risiko (JS-Abhaengigkeiten) ist dokumentiert und adressierbar.
- **Phase 3 (Settings/Mail):** smtplib ist stdlib, gut dokumentiert. Fernet-Verschluesselung ist Standard-Pattern.
- **Phase 4 (Scheduler):** Flask-APScheduler-Pattern ist dokumentiert. Single-Worker-Constraint ist bekannte Loesung.

Kein Phase benoetigt vertieftes Research-Phase — alle Patterns sind gut etabliert und Quellen sind verifiziert.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Alle Versionen via PyPI verifiziert; Werkzeug bereits installiert; Tailwind Play CDN Production-Warnung aus offizieller Doku bestaetigt |
| Features | HIGH | Flask-Oekosystem gut dokumentiert; Feature-Dependencies logisch abgeleitet; Anti-Features begruendet durch konkrete Nachteile |
| Architecture | HIGH | App-Factory + Blueprint-Pattern ist Flask-Standard (Miguel Grinberg Mega-Tutorial); smtplib statt Flask-Mail ist pragmatische Entscheidung mit klarer Begruendung |
| Pitfalls | HIGH | Projektspezifisch — basierend auf Codebasis-Analyse (app.py, docker-compose.yml); Watchtower + SQLite + APScheduler-Risiken sind bekannte Community-Patterns |

**Overall confidence:** HIGH

### Gaps to Address

- **Fernet-Verschluesselung fuer smtp_pass:** Bibliothek `cryptography` noch nicht in requirements.txt — muss in Phase 3 ergaenzt werden. Alternativ: dokumentierter Verzicht mit Hinweis auf Risiko.
- **ChurchDesk-API-Tokens bleiben in ENV fuer v2.0:** Bewusste Entscheidung — Tokens werden nicht in DB migriert. Falls kuenftig gewuenscht: UserSettings bekommt Feld `churchdesk_token`; ist fuer v2.0 kein Blocker.
- **APScheduler vs. externer Cron:** Falls Gunicorn in Zukunft mit mehreren Workern betrieben werden soll, muss der Scheduler in einen externen Cron-Job (systemd-Timer oder Host-Cron) ausgelagert werden. Fuer v2.0 mit Single-Worker: kein Problem.
- **Test-Mail-Button in Settings:** PITFALLS.md empfiehlt "Test-Mail senden"-Button in Settings (Integration Gotcha). Ist nicht explizit in FEATURES.md als v2.0-Feature aufgefuehrt — sollte beim Settings-Blueprint erwaegt werden.

## Sources

### Primary (HIGH confidence)
- https://pypi.org/project/Flask-Login/ — Version 0.6.3 verifiziert, Flask 3 Kompatibilitaet
- https://pypi.org/project/Flask-SQLAlchemy/ — Version 3.1.1 verifiziert
- https://pypi.org/project/Flask-Migrate/ — Version 4.1.0, Januar 2025, SQLite batch-mode
- https://pypi.org/project/Flask-Mail/ — Version 0.10.0, Mai 2024
- https://pypi.org/project/Flask-WTF/ — Version 1.2.2, Oktober 2024
- https://tailwindcss.com/docs/installation/play-cdn — "not intended for production" verifiziert
- https://flask.palletsprojects.com/en/stable/patterns/appfactories/ — App Factory Pattern
- https://flask-login.readthedocs.io/en/latest/ — Flask-Login Doku
- https://flask-sqlalchemy.readthedocs.io/en/stable/ — Flask-SQLAlchemy Doku

### Secondary (MEDIUM confidence)
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins — Blueprint + Login Pattern
- https://blog.miguelgrinberg.com/post/how-to-add-flask-migrate-to-an-existing-project — Migrate zu bestehendem Projekt
- https://viniciuschiele.github.io/flask-apscheduler/ — APScheduler Flask-Integration
- Codebasis-Analyse: web/app.py, web/config.py, web/docker-compose.yml (projektspezifisch)

### Tertiary (verweist auf zu validierende Details)
- https://pypi.org/project/Flask-Bcrypt/ — Deprecation-Status (MEDIUM confidence — letztes Release April 2022, aber kein offizielles Deprecation-Statement)

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
