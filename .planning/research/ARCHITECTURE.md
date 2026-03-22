# Architecture Research

**Domain:** Flask Web App — Auth, DB, Scheduled Tasks, Settings
**Researched:** 2026-03-22
**Confidence:** HIGH

## Standard Architecture

### System Overview: v2.0 Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser / Client                         │
│  GET/POST Requests         Session Cookie       Flash Messages   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                          Flask App (app.py)                       │
│                     create_app() Factory Pattern                  │
├──────────────┬───────────────────────────────┬───────────────────┤
│ auth/         │ main/                         │ settings/         │
│ Blueprint     │ Blueprint                     │ Blueprint         │
│               │                               │                   │
│ /login        │ / (index)                     │ /settings         │
│ /logout       │ /fetch_churchdesk_events      │ /settings/orgs    │
│ /admin/users  │ /export_selected_events       │ /settings/mail    │
│               │ /download                     │                   │
│               │ /health                       │                   │
└──────┬────────┴───────────────────────────────┴──────────┬────────┘
       │                                                    │
┌──────▼────────────────────────────┐   ┌──────────────────▼────────┐
│         Service Layer              │   │     Scheduler Layer        │
│  formatting.py (unchanged)        │   │  APScheduler (in-process)  │
│  churchdesk_api.py (unchanged)    │   │  monthly_email_job()       │
│  mail_service.py (NEW)            │   │  → reads DB for user prefs │
│  user_service.py (NEW)            │   │  → calls mail_service.py   │
└──────────────────┬────────────────┘   └───────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────────────────┐
│                        Data Layer (SQLite)                          │
├─────────────────────┬──────────────────────────────────────────────┤
│  users table         │  user_settings table                         │
│  id, username,       │  user_id (FK), churchdesk_org_ids,           │
│  password_hash,      │  mail_recipient, mail_smtp_host,             │
│  is_admin,           │  mail_smtp_port, mail_smtp_user,             │
│  created_at          │  mail_smtp_pass, mail_enabled,               │
│                      │  auto_send_day_of_month                      │
└─────────────────────┴──────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Status |
|-----------|----------------|--------|
| `app.py` (create_app) | App factory, extension init, blueprint registration | MODIFY |
| `auth/routes.py` | Login, logout, admin user management | NEW |
| `main/routes.py` | Core formatter routes (moved from app.py) | REFACTOR |
| `settings/routes.py` | User settings CRUD | NEW |
| `models.py` | SQLAlchemy User + UserSettings models | NEW |
| `mail_service.py` | Dynamic SMTP send using per-user settings | NEW |
| `formatting.py` | Pure formatting functions | UNCHANGED |
| `churchdesk_api.py` | ChurchDesk API client | UNCHANGED |
| `config.py` | Org loader from ENV (still used for initial seeding) | MINOR MODIFY |
| `scheduler.py` | APScheduler setup, monthly email job | NEW |
| `templates/` | Jinja2 templates — new auth + settings templates | EXTEND |

## Recommended Project Structure

```
web/
├── app.py                   # create_app() factory — MODIFIED
├── models.py                # SQLAlchemy models: User, UserSettings — NEW
├── extensions.py            # db, login_manager, scheduler instances — NEW
├── scheduler.py             # APScheduler job definitions — NEW
├── mail_service.py          # Per-user SMTP email sending — NEW
├── formatting.py            # Pure functions — UNCHANGED
├── churchdesk_api.py        # API client — UNCHANGED
├── config.py                # ENV-based org loader — MINOR MODIFY
│
├── auth/                    # Auth blueprint — NEW
│   ├── __init__.py
│   └── routes.py            # /login, /logout, /admin/users
│
├── main/                    # Main blueprint — REFACTORED from app.py
│   ├── __init__.py
│   └── routes.py            # /, /fetch_churchdesk_events, /export, /download, /health
│
├── settings/                # Settings blueprint — NEW
│   ├── __init__.py
│   └── routes.py            # /settings, /settings/orgs, /settings/mail
│
├── templates/
│   ├── base.html            # MODIFY: add nav with login state
│   ├── auth/
│   │   └── login.html       # NEW
│   ├── main/
│   │   ├── index.html       # MOVE + MODIFY
│   │   ├── churchdesk_events.html  # MOVE
│   │   └── result.html      # MOVE
│   └── settings/
│       └── settings.html    # NEW
│
├── migrations/              # Flask-Migrate — NEW (auto-generated)
├── requirements.txt         # ADD: Flask-Login, Flask-SQLAlchemy, Flask-Migrate,
│                            #      Flask-APScheduler, Werkzeug (bcrypt)
└── docker-compose.yml       # ADD: volume for SQLite file, SECRET_KEY env
```

### Structure Rationale

- **extensions.py:** Vermeidet zirkulaere Imports — db, login_manager, scheduler werden hier instanziiert, aber erst in create_app() an die App gebunden (init_app Pattern).
- **Blueprints (auth/, main/, settings/):** Jede Verantwortlichkeit in eigener Registrierungseinheit. main/ enthaelt alles was schon in app.py war — minimaler Refactor-Aufwand.
- **models.py flach (kein models/):** App ist klein. Ein Modul reicht voellig aus.
- **migrations/:** Von Flask-Migrate generiert, ins Git einchecken.

## Architectural Patterns

### Pattern 1: App Factory mit init_app()

**Was:** Flask-App wird in einer Funktion `create_app()` gebaut statt global. Extensions wie `db`, `login_manager` und `scheduler` werden als Modul-Variablen instanziiert, aber erst in der Factory per `init_app(app)` an die App gebunden.

**Wann:** Immer wenn Extensions hinzukommen, besonders wenn Tests die App mehrfach mit unterschiedlicher Konfig brauchen.

**Trade-offs:** Etwas mehr Boilerplate. Verhindert aber zirkulaere Imports und ermoeglicht saubere Tests.

**Beispiel:**
```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()

# app.py
from extensions import db, login_manager, scheduler

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    from auth import bp as auth_bp
    from main import bp as main_bp
    from settings import bp as settings_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)

    return app
```

### Pattern 2: Flask-Login mit UserMixin

**Was:** User-Model erbt von `UserMixin` (liefert `is_authenticated`, `is_active`, `get_id()`). `@login_required` Decorator sichert alle Routes ausser Login.

**Wann:** Alle Routes in main/ und settings/ werden mit `@login_required` geschuetzt. Login-View ist die einzige ungeschuetzte Route.

**Trade-offs:** Minimal. Flask-Login ist das Standard-Tool fuer Flask-Auth — kein Overhead.

**Beispiel:**
```python
# models.py
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    mail_recipient = db.Column(db.String(256))
    mail_smtp_host = db.Column(db.String(256))
    mail_smtp_port = db.Column(db.Integer, default=587)
    mail_smtp_user = db.Column(db.String(256))
    mail_smtp_pass = db.Column(db.String(256))  # verschluesseln (Fernet)
    mail_enabled = db.Column(db.Boolean, default=False)
    auto_send_day = db.Column(db.Integer, default=25)
    churchdesk_org_ids = db.Column(db.Text)  # JSON-kodiert: "[2596, 6572]"
    user = db.relationship('User', back_populates='settings')
```

### Pattern 3: Dynamisches SMTP aus DB-Settings

**Was:** Flask-Mail wird NICHT global konfiguriert. Stattdessen baut `mail_service.py` einen `smtplib`-basierten Client zur Laufzeit aus den gespeicherten UserSettings.

**Wann:** Notwendig weil Mail-Einstellungen pro User in der DB liegen — Flask-Mail ist auf App-Konfiguration ausgelegt, nicht auf Runtime-Wechsel.

**Trade-offs:** Etwas mehr Code als Flask-Mail, aber volle Kontrolle. `smtplib` ist stdlib — keine Extra-Dependency.

**Beispiel:**
```python
# mail_service.py
import smtplib
from email.mime.text import MIMEText

def send_boyens_email(user_settings, subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = user_settings.mail_smtp_user
    msg['To'] = user_settings.mail_recipient

    with smtplib.SMTP(user_settings.mail_smtp_host, user_settings.mail_smtp_port) as server:
        server.starttls()
        server.login(user_settings.mail_smtp_user, decrypt(user_settings.mail_smtp_pass))
        server.send_message(msg)
```

### Pattern 4: APScheduler fuer monatlichen Mail-Versand

**Was:** Flask-APScheduler laeuft in-process. Ein CronJob lauft taeglich und prueft ob heute der konfigurierte Versand-Tag eines Users ist.

**Wann:** Genau richtig fuer diesen Use Case — ein Mail-Versand pro Monat pro User, kein verteiltes System noetig.

**Wichtig:** Docker-Compose muss `deploy: replicas: 1` sicherstellen — APScheduler 3.x unterstuetzt nur einen Worker-Prozess.

**Beispiel:**
```python
# scheduler.py
from extensions import scheduler
from models import User

def register_jobs(app):
    @scheduler.task('cron', id='monthly_email_check', hour=8, minute=0)
    def monthly_email_check():
        with app.app_context():
            from datetime import date
            today = date.today()
            users = User.query.filter(User.settings != None).all()
            for user in users:
                s = user.settings
                if s.mail_enabled and s.auto_send_day == today.day:
                    # generate output for user's orgs and send
                    send_for_user(user, today.year, today.month)
```

## Data Flow

### Request Flow: Login

```
POST /login (username, password)
    ↓
auth/routes.py → User.query.filter_by(username=...) → verify password_hash
    ↓ success
login_user(user) → Flask session cookie gesetzt
    ↓
redirect → / (index)
```

### Request Flow: Formatter (geschuetzt)

```
@login_required
POST /fetch_churchdesk_events (year, month, orgs)
    ↓
current_user (Flask-Login) verfuegbar
    ↓
main/routes.py → churchdesk_api.py → EventAnalyzer
    ↓
formatting.py → convert_to_boyens()
    ↓
render_template('main/churchdesk_events.html', events=...)
```

### Request Flow: Settings speichern

```
POST /settings/mail (smtp_host, smtp_port, ...)
    ↓
@login_required
settings/routes.py → UserSettings.query.filter_by(user_id=current_user.id)
    ↓
update fields → encrypt smtp_pass → db.session.commit()
    ↓
flash('Gespeichert') → redirect /settings
```

### Scheduler Flow: Automatischer Versand

```
APScheduler CronJob (taeglich 08:00)
    ↓
monthly_email_check()
    ↓
User.query.all() → filter mail_enabled=True AND auto_send_day == today.day
    ↓ fuer jeden matching User:
ChurchDeskAPI.get_monthly_events(orgs_from_settings)
    ↓
convert_to_boyens()
    ↓
mail_service.send_boyens_email(user_settings, ...)
    ↓
db: log send attempt (optional)
```

## Build Order (Dependency-gesteuert)

Die Reihenfolge ist kritisch — spaetere Komponenten bauen auf frueheren auf:

| Schritt | Was | Warum zuerst |
|---------|-----|--------------|
| 1 | App Factory + extensions.py | Fundament — alles haengt davon ab |
| 2 | SQLAlchemy Models + Flask-Migrate | DB-Schema muss vor Auth existieren |
| 3 | Flask-Login + auth Blueprint | Login braucht User-Model |
| 4 | @login_required auf alle main/ Routes | Auth muss fertig sein bevor geschuetzt wird |
| 5 | Settings Blueprint + UserSettings CRUD | Braucht eingeloggten User (current_user) |
| 6 | mail_service.py (smtplib) | Braucht UserSettings-Daten aus DB |
| 7 | APScheduler + monatlicher Job | Braucht mail_service + UserSettings |
| 8 | Admin: User-Verwaltung | Braucht fertiges Auth-System |

## Integration Points

### Bestehende Komponenten — unveraendert

| Komponente | Integrationsart | Hinweis |
|------------|----------------|---------|
| `formatting.py` | Direkter Import | Bleibt pure functions — kein Flask-Context noetig |
| `churchdesk_api.py` | Direkter Import | API-Tokens weiterhin aus ENV (oder kuenftig aus UserSettings) |
| `config.py` (ORGANIZATIONS) | Import in main/routes.py | Weiterhin ENV-basiert fuer v2.0 |

### Neue externe Abhaengigkeiten

| Service | Integrationsart | Hinweis |
|---------|----------------|---------|
| SQLite (Datei) | Flask-SQLAlchemy | Volume-Mount in Docker notwendig: `./data:/app/data` |
| SMTP-Server | smtplib (stdlib) | Konfiguriert pro User in UserSettings, kein globaler ENV |
| APScheduler | Flask-APScheduler | In-process, kein Redis/Celery — passt fuer diesen Scale |

### Interne Grenzen

| Grenze | Kommunikation | Hinweis |
|--------|--------------|---------|
| Blueprints ↔ DB | SQLAlchemy ORM via `from models import User` | Kein db-Context ausserhalb Request — `with app.app_context()` im Scheduler |
| Scheduler ↔ Flask | `app.app_context()` im Job-Body | APScheduler laeuft ausserhalb des Request-Contexts |
| Settings ↔ Mail | Direkte Objekt-Uebergabe | `send_boyens_email(user.settings, ...)` — kein globaler State |

## Anti-Patterns

### Anti-Pattern 1: Flask-Mail global mit ENV konfigurieren

**Was gemacht wird:** `MAIL_SERVER`, `MAIL_PASSWORD` in ENV setzen, Flask-Mail global initialisieren.
**Warum falsch:** Settings sollen pro User in der DB liegen. Globale Flask-Mail-Config laesst keinen Runtime-Wechsel zu ohne Hacks.
**Stattdessen:** `smtplib` direkt in `mail_service.py` mit per-User Credentials aus `UserSettings`.

### Anti-Pattern 2: Celery fuer monatliche Mail

**Was gemacht wird:** Redis + Celery Worker Container hinzufuegen fuer den Scheduler.
**Warum falsch:** Massiver Overhead fuer einen Job pro Monat pro User. Docker-Compose wuerde 3 zusaetzliche Services brauchen.
**Stattdessen:** Flask-APScheduler in-process — genuegt vollstaendig fuer diesen Use Case.

### Anti-Pattern 3: ENV-Vars fuer SMTP-Credentials behalten

**Was gemacht wird:** SMTP-Credentials weiterhin in docker-compose.yml ENV-Section.
**Warum falsch:** Widerspruch zur v2.0-Anforderung "Mail-Konfiguration pro User, NICHT in ENV-Vars".
**Stattdessen:** Settings-Formular im Web-Interface, verschluesselt in `user_settings.mail_smtp_pass` (Fernet-Verschluesselung mit APP_KEY).

### Anti-Pattern 4: Globale app-Variable beibehalten

**Was gemacht wird:** `app = Flask(__name__)` auf Modulebene lassen (aktuelle v1.0-Struktur).
**Warum falsch:** Zirkulaere Imports beim Einbinden von extensions.py, models.py und Blueprints.
**Stattdessen:** `create_app()` Factory — einmalige Umstrukturierung, die alle weiteren Schritte vereinfacht.

### Anti-Pattern 5: Mehrere APScheduler Worker

**Was gemacht wird:** `docker compose up --scale web=2` oder Gunicorn mit mehreren Workers.
**Warum falsch:** APScheduler 3.x kennt nur einen Process — Jobs wuerden mehrfach ausgefuehrt.
**Stattdessen:** Single Worker in docker-compose.yml explizit sicherstellen. In Produktionsumgebung: `SCHEDULER_API_ENABLED=False`, nur ein Gunicorn-Worker.

## Skalierungsbetrachtung

| Scale | Architektur-Anpassung |
|-------|----------------------|
| 1-10 User (aktueller Use Case) | SQLite + Flask-APScheduler in-process — perfekt passend |
| 10-100 User | SQLite reicht weiterhin; APScheduler bleibt stabil |
| 100+ User | Migration zu PostgreSQL, Celery erwaegen — fuer diesen Kirchenkreis nicht relevant |

### Erste Engpaesse (wenn relevant)

1. **SQLite Write-Locks:** Mehrere gleichzeitige Schreibzugriffe. Mitigation: WAL-Mode aktivieren (`PRAGMA journal_mode=WAL`). Bei >20 concurrent Writern: PostgreSQL.
2. **APScheduler bei Multi-Worker:** Sofort wenn Gunicorn >1 Worker gestartet wird. Mitigation: Explizit `workers=1` in Gunicorn-Config.

## Sources

- [Flask Application Factories — offizielle Doku](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Flask-Login Doku (0.6.x)](https://flask-login.readthedocs.io/en/latest/)
- [Flask-SQLAlchemy Doku (3.1.x)](https://flask-sqlalchemy.readthedocs.io/en/stable/)
- [Flask-Migrate — How To Add to Existing Project](https://blog.miguelgrinberg.com/post/how-to-add-flask-migrate-to-an-existing-project)
- [Flask-APScheduler GitHub + Doku](https://viniciuschiele.github.io/flask-apscheduler/)
- [Flask Mega-Tutorial Part V: User Logins (Grinberg)](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins)
- [Flask Mega-Tutorial Part X: Email Support](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support)
- [Structuring Large Flask Apps with Blueprints](https://www.section.io/engineering-education/structuring-large-applications-with-blueprints-and-application-factory-in-flask/)

---
*Architecture research for: Gottesdienst-Formatter v2.0 — Auth, DB, Scheduler, Settings*
*Researched: 2026-03-22*
