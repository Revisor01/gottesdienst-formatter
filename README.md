# Gottesdienst-Formatter für Boyens Medien

Web-Anwendung des ev.-luth. Kirchenkreises Dithmarschen, die Gottesdiensttermine aus
ChurchDesk und Excel-Dateien in exakt formatierte Fließtexte für Boyens Medien umwandelt.

**Core Value:** Der Output muss 1:1 der Boyens-Fließtext-Vorgabe entsprechen — ohne
redaktionelle Nacharbeit übernehmbar.

**Live:** http://gd.kkd-fahrtenbuch.de

## Features

- **ChurchDesk-Anbindung** — Termine direkt aus der ChurchDesk-API v3.0.0 holen,
  über mehrere Organisationen (Kirchspiele/Gemeinden) hinweg
- **Excel-Upload** — alternativ .xlsx-Dateien einlesen
- **Boyens-Formatierung** — Datumsgruppierung, deutsche Wochentage/Monate,
  Abkürzungen (`Gd.`, `Gd. m. A.`, `P.`, `Pn.`), Orts-Regeln für Multi-Kirchen-Orte
- **Benutzerverwaltung** — Login (Flask-Login), Admin-Bereich
- **Admin-Oberfläche** — Organisationen, Personen/Pastor:innen, Gottesdiensttypen
  und Orts-Regeln pflegen
- **Automatischer Mailversand** — Scheduler verschickt den Monatsauszug an die Redaktion
- **Export** — Download als .txt oder Copy-to-Clipboard

## Ausgabeformat

```
Sonntag, 1. Juni:
Albersdorf, St. Remigius Kirche: 9.30 Uhr, Gd., P. Keppel
Büsum, St. Clemens-Kirche: 9.30 Uhr, Gd. m. A., Pn. Verwold
```

## Architektur

Flask-App mit Blueprints, SQLite-Datenbank, Alembic-Migrationen:

```
web/
├── app.py                 # App-Factory (create_app)
├── config.py              # Organisationen aus der DB laden
├── models.py              # SQLAlchemy-Modelle
├── formatting.py          # Boyens-Formatierungslogik
├── churchdesk_api.py      # ChurchDesk-API-Client (Single + Multi-Org)
├── mail_service.py        # Mailversand
├── scheduler.py           # Automatischer Monatsversand
├── crypto.py              # Verschlüsselung der Mail-Zugangsdaten
├── main/ auth/ admin/ settings/   # Blueprints
├── migrations/            # Alembic
├── templates/  static/
└── tests/                 # pytest
gottesdienst_formatter_final.py    # Standalone-CLI (Excel → Text)
```

Organisationen und ihre API-Tokens liegen in der Datenbank (Tabelle `organizations`)
und werden über den Admin-Bereich gepflegt — **nicht** im Code.

## Lokaler Start

```bash
cd web
cp .env.example .env          # SECRET_KEY + ChurchDesk-Tokens eintragen
pip install -r requirements.txt
flask db upgrade
python -c "from app import create_app; create_app().run(debug=True)"
```

`SECRET_KEY` ist Pflicht — die App startet ohne ihn bewusst nicht:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Tests

```bash
cd web
pip install -r requirements-dev.txt
pytest
```

Der Goldstandard-Test (`tests/test_boyens_goldstandard.py`) prüft den Output gegen
eine Referenzdatei — er ist die Absicherung gegen Formatierungs-Regressionen.

### Tailwind CSS

```bash
npm install
npm run tw:build      # oder: npm run tw:watch
```

## Deployment

Docker auf `185.248.143.234`, Pfad `/opt/gottesdienst-formatter`.
Container-Port 5000 → Host 5001, davor ein Reverse Proxy.

```bash
git add . && git commit -m "..." && git push && \
ssh root@185.248.143.234 "cd /opt/gottesdienst-formatter && git pull origin main && \
cd web && docker compose build && docker compose down && docker compose up -d"
```

Persistente Daten liegen in `web/data/` (SQLite) — das Volume `./data:/app/data` ist
zwingend, sonst geht die Datenbank bei jedem Rebuild verloren.

## Konfiguration

Alle Werte über Environment-Variablen bzw. `.env` (siehe `.env.example`):

| Variable | Bedeutung |
|---|---|
| `SECRET_KEY` | Flask-Session-Key (Pflicht, kein Fallback) |
| `CHURCHDESK_ORG_IDS` | Kommaliste der Organisations-IDs |
| `CHURCHDESK_ORG_<ID>_TOKEN` | API-Token je Organisation |
| `CHURCHDESK_ORG_<ID>_NAME` | Anzeigename je Organisation |
| `FLASK_ENV` / `FLASK_DEBUG` | `production` / `false` |

## Excel-Datenformat

| Spalte | Beschreibung | Beispiel |
|--------|-------------|----------|
| Startdatum | Datum und Uhrzeit | 2025-06-01 09:30:00 |
| Titel | Gottesdiensttyp | Gottesdienst, Abendmahl |
| Standortnamen | Kirche/Ort | Albersdorf, St. Remigius Kirche |
| Mitwirkender | Pastor/Pastorin | Pastor Keppel |
| Gemeinden | Gemeinde (Fallback) | Albersdorf |

## Anforderungen Boyens Medien

- Termine nach Datum sortiert und zusammengefasst
- Format: „Ort: Zeit, Gottesdiensttyp, Pastor"
- Bei mehreren Kirchen pro Ort: Kirchenname angeben
- Keine Tabellen oder zusätzliche Formatierung
- Deadline: bis zum 20. des Vormonats

## Lizenz

© 2025–2026 Pastor Simon Luthe, Kirchenkreis Dithmarschen —
entwickelt für den internen Gebrauch des Kirchenkreises Dithmarschen.
