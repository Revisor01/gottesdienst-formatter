# Stack Research

**Domain:** Flask web app — Authentication, User Settings, Auto-Email, UI Makeover
**Researched:** 2026-03-22
**Confidence:** HIGH (verifiziert via PyPI, offizielle Docs)

## Scope

Nur neue Bibliotheken für v2.0. Bestehender Stack (Flask 2.3.3, pandas, requests, openpyxl, Werkzeug, pytz) bleibt unverändert.

---

## Recommended Stack

### Authentication & User Management

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Flask-Login | 0.6.3 | Session-Management, `current_user`, `@login_required` | Standard für Flask-Auth — minimal, gut integriert, Pallets Ecosystem |
| Flask-SQLAlchemy | 3.1.1 | ORM für User-Modell und Settings-Persistenz | Offizielle Flask-Erweiterung, funktioniert direkt mit Flask-Login |
| Werkzeug security | (bereits installiert) | Passwort-Hashing (`generate_password_hash`, `check_password_hash`) | Bereits Abhängigkeit, kein zusätzliches Paket nötig |

Passwort-Hashing direkt über Werkzeug (bereits Abhängigkeit) — kein Flask-Bcrypt nötig. Werkzeug nutzt scrypt/pbkdf2 by default, sicher genug für interne Firmen-App.

### Datenbank

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| SQLite | (stdlib) | Datenbank für User + Settings | Kein separater DB-Server, passt zu Docker-Volume-Deployment, ausreichend für ~10 User |
| Flask-Migrate | 4.1.0 | Schema-Migrationen via Alembic | Ab v4.0 automatisch SQLite-kompatibel (batch-mode), schützt vor manuellen Schema-Änderungen |

SQLite in einem Docker-Volume ist die richtige Wahl — kein PostgreSQL-Overhead für eine interne App mit wenigen Nutzern. Flask-Migrate v4.1.0 hat explizit `render_as_batch=True` für SQLite aktiviert (keine SQLite-ALTER-Probleme mehr).

### E-Mail

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Flask-Mail | 0.10.0 | SMTP-E-Mail-Versand | Pallets Ecosystem, aktiv maintained (Release Mai 2024), minimal und direkt integrierbar |

Flask-Mail erlaubt Konfiguration per App-Config zur Laufzeit (aus DB laden, pro User), was genau dem Anforderungsprofil entspricht (Mail-Settings in DB, nicht ENV).

### UI Framework

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Tailwind CSS CLI | v4.x | CSS-Framework, grüne Farbpalette | Kein JavaScript-Framework nötig, utility-first passt zu Jinja2-Templates, Build-Artefakt in static/ |

Tailwind CLI (npm-basiert, Build-Schritt) statt CDN. Die Play CDN ist laut offizieller Doku explizit "not intended for production". Das kompilierte CSS-File liegt in `static/css/` und wird von Flask served.

### Formulare & CSRF

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Flask-WTF | 1.2.2 | CSRF-Schutz für Login-Formular und Settings | Pallets Ecosystem, standard für Flask-Forms, Release Oktober 2024 |

---

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Flask-Migrate | 4.1.0 | DB-Migrationen | Immer wenn sich User-Model oder Settings-Schema ändert |
| python-dotenv | aktuell | `.env`-Support für SMTP-Credentials als Fallback | Für lokale Entwicklung — Prod nutzt DB-Settings |

---

## Installation

```bash
# In web/requirements.txt hinzufügen:
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-Mail==0.10.0
Flask-WTF==1.2.2
Flask-Migrate==4.1.0

# Dev-Build für Tailwind CSS (außerhalb des Docker-Containers):
npm install -D tailwindcss@latest
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

Tailwind-Build läuft lokal und das kompilierte `output.css` wird ins Docker-Image eingebaut — kein Node.js im Container nötig.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Flask-Login | Flask-Security-Too | Wenn OAuth, 2FA, oder Role-based Access benötigt wird — deutlich mehr Overhead |
| Flask-Login | Flask-JWT-Extended | Nur wenn API-first (kein Session-Cookie) — für Browser-App unnötig |
| SQLite + Flask-Migrate | PostgreSQL | Wenn >100 concurrent User oder komplexe Queries — hier nicht der Fall |
| Flask-Mail | Celery + Redis + Flask-Mail | Wenn asynchroner Versand und Queuing nötig — hier synchroner Versand ausreichend |
| Tailwind CLI | Bootstrap | Wenn kein Build-Schritt gewünscht — aber schlechter für Custom-Grün-Design |
| Tailwind CLI | Tailwind Play CDN | Nur für Prototyping — explizit nicht für Produktion |
| Werkzeug security | Flask-Bcrypt | Flask-Bcrypt ist seit 2022 nicht mehr aktiv gewartet; Werkzeug bietet gleichwertiges Hashing |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Tailwind Play CDN in Produktion | Offiziell "not for production" — kein Tree-shaking, langsam | Tailwind CLI Build-Schritt |
| Flask-Bcrypt | Letztes Release April 2022, nicht aktiv gewartet | `werkzeug.security` — bereits installiert |
| PostgreSQL | Infrastruktur-Overhead ohne Mehrwert bei <20 Nutzern | SQLite in Docker-Volume |
| Celery/Redis für Mail | Massive Complexity für synchrones Monatsmailing | Flask-Mail direkt |
| Flask-Security-Too | Bringt 10x mehr Features als nötig (OAuth, 2FA, Tokens) | Flask-Login + Werkzeug |

---

## Stack Patterns by Variant

**Da Mail-Settings pro User in DB gespeichert werden (nicht ENV):**
- Flask-Mail-Konfiguration dynamisch aus DB laden vor jedem Mail-Versand
- `app.config.update(MAIL_SERVER=user.mail_server, ...)` vor `mail.send(msg)`
- Nicht die globale App-Config für SMTP nutzen

**Da SQLite in Docker-Volume:**
- Volume-Mount: `./data:/app/data` (DB-Datei außerhalb des Containers)
- DB-Pfad: `sqlite:////app/data/app.db`
- Bei Container-Rebuild bleibt DB erhalten

**Da Tailwind-Build außerhalb des Containers:**
- `output.css` wird im Repo versioniert (oder im CI-Build generiert)
- Kein Node.js im Dockerfile nötig
- GitHub Actions kann Build-Schritt übernehmen

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Flask-Login 0.6.3 | Flask 2.3.x, Werkzeug 2.3.x | Explizit für Flask 3 + Werkzeug 3 kompatibel gemacht |
| Flask-SQLAlchemy 3.1.1 | Flask 2.3.x, SQLAlchemy 2.x | Erfordert SQLAlchemy 2.0+ API |
| Flask-Migrate 4.1.0 | Flask-SQLAlchemy 3.x, Alembic | v4.0+ automatisch SQLite batch-mode |
| Flask-Mail 0.10.0 | Flask 2.x | Pallets Ecosystem, aktiv gewartet |
| Flask-WTF 1.2.2 | Flask 2.x, WTForms 3.x | Aktuelles Release Oktober 2024 |

---

## Sources

- https://pypi.org/project/Flask-SQLAlchemy/ — Version 3.1.1 verifiziert
- https://pypi.org/project/Flask-Mail/ — Version 0.10.0, Release Mai 2024 verifiziert
- https://pypi.org/project/Flask-Migrate/ — Version 4.1.0, Release Januar 2025 verifiziert
- https://github.com/maxcountryman/flask-login/blob/main/CHANGES.md — Version 0.6.3, Flask 3 Kompatibilität verifiziert
- https://flask-login.readthedocs.io/en/latest/ — 0.7.0 Doku (noch unreleased/dev)
- https://tailwindcss.com/docs/installation/play-cdn — "not intended for production" verifiziert
- https://pypi.org/project/Flask-WTF/ — Version 1.2.2, Release Oktober 2024 (Websuche)
- https://pypi.org/project/Flask-Bcrypt/ — Version 1.0.1, letztes Release April 2022 — MEDIUM confidence für Deprecation-Status

---
*Stack research for: Flask Auth / Settings / Email / UI — Gottesdienst-Formatter v2.0*
*Researched: 2026-03-22*
