<h1 align="center">Gottesdienst-Formatter</h1>

<p align="center">
  Gottesdiensttermine aus ChurchDesk oder Excel als fertiger Fließtext<br>
  für die Gottesdienstseite der Tageszeitung — ohne Nacharbeit.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776ab?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-SQLite-000000?logo=flask" alt="Flask">
  <img src="https://img.shields.io/github/license/Revisor01/gottesdienst-formatter" alt="Lizenz">
</p>

## Worum es geht

Jeden Monat drucken die Zeitungen von Boyens Medien die Gottesdienste im
Kirchenkreis Dithmarschen ab — als Fließtext in einem genau festgelegten
Format. Die Termine liegen in ChurchDesk, über viele Gemeinden verteilt.
Sie von Hand abzuschreiben und zu kürzen kostet Stunden und erzeugt Fehler.

Der Gottesdienst-Formatter holt die Termine selbst, bringt sie in das
geforderte Format und verschickt den Monatsauszug auf Wunsch an die Redaktion.

## Funktionen

- **ChurchDesk-Anbindung** — Termine direkt aus der ChurchDesk-API, über
  mehrere Organisationen (Kirchspiele, Gemeinden) hinweg
- **Excel-Import** — alternativ eine `.xlsx`-Datei hochladen
- **Formatierung nach Vorgabe** — nach Datum gruppiert, deutsche Wochentage
  und Monate, Abkürzungen (`Gd.`, `Gd. m. A.`, `P.`, `Pn.`), Kirchenname nur
  dort, wo ein Ort mehrere Kirchen hat
- **Verwaltung** — Organisationen, Pastor:innen, Gottesdiensttypen und
  Orts-Regeln im Admin-Bereich pflegen
- **Monatsversand** — der Auszug geht automatisch per E-Mail an die Redaktion
- **Export** — Download als `.txt` oder in die Zwischenablage

So sieht das Ergebnis aus:

```
Sonntag, 1. Juni:
Albersdorf, St. Remigius Kirche: 9.30 Uhr, Gd., P. Keppel
Büsum, St. Clemens-Kirche: 9.30 Uhr, Gd. m. A., Pn. Verwold
```

### Excel-Format

| Spalte | Inhalt | Beispiel |
|--------|--------|----------|
| Startdatum | Datum und Uhrzeit | 2025-06-01 09:30:00 |
| Titel | Gottesdiensttyp | Gottesdienst, Abendmahl |
| Standortnamen | Kirche und Ort | Albersdorf, St. Remigius Kirche |
| Mitwirkender | Pastor:in | Pastor Keppel |
| Gemeinden | Gemeinde (Ersatz, wenn kein Standort) | Albersdorf |

Für einzelne Excel-Dateien gibt es auch ein Skript für die Kommandozeile,
ganz ohne Server; siehe [ANLEITUNG.md](ANLEITUNG.md).

## Versionen

Was sich wann geändert hat, steht in [CHANGELOG.md](CHANGELOG.md) — nach
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/), aus Sicht der
Nutzer:innen geschrieben. Die
[Releases](https://github.com/Revisor01/gottesdienst-formatter/releases)
fassen jede Version zusammen.

## Selbst betreiben

**Mit Docker.** Jeder Stand auf `main` liegt als fertiges Image unter
`ghcr.io/revisor01/gottesdienst-formatter`. Die Datei
[web/docker-compose.prod.yml](web/docker-compose.prod.yml) startet es auf
Port 5001:

```bash
cd web
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec gottesdienst-formatter flask create-admin admin
```

Beim Start führt der Container die Datenbank-Migrationen aus. Die Datenbank
(SQLite) liegt in `web/data/` — dieses Verzeichnis muss als Volume erhalten
bleiben, sonst ist sie nach jedem Neustart leer. Die Compose-Datei startet
außerdem Watchtower, das neue Images selbst nachzieht.

**Lokal zum Entwickeln** (Python 3.11):

```bash
git clone https://github.com/Revisor01/gottesdienst-formatter.git
cd gottesdienst-formatter/web
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
pip install -r requirements.txt
flask db upgrade
flask create-admin admin
python -c "from app import create_app; create_app().run(debug=True)"
```

| Variable | Pflicht | Bedeutung |
|----------|---------|-----------|
| `SECRET_KEY` | ja | Schlüssel für Sitzungen; aus ihm wird auch der Schlüssel für die gespeicherten Mail-Zugangsdaten abgeleitet. Ohne ihn startet die App nicht, wechselt er, müssen die Mail-Zugangsdaten neu eingetragen werden |
| `CHURCHDESK_ORG_<ID>_TOKEN` | nein | API-Token je Organisation; nur beim ersten `flask db upgrade` gelesen, danach im Admin-Bereich gepflegt |
| `FLASK_ENV`, `FLASK_DEBUG` | nein | `production` und `false` im Betrieb |

Der Mailversand (SMTP-Server, Empfänger, Versandtag im Monat) wird in der
Oberfläche eingerichtet.

## Aufbau

```
gottesdienst-formatter
├── web/
│   ├── app.py              — App-Factory, Befehl create-admin
│   ├── formatting.py       — Regeln des Zeitungsformats
│   ├── churchdesk_api.py   — ChurchDesk-Client für eine oder mehrere Organisationen
│   ├── scheduler.py        — monatlicher Versand
│   ├── main/ auth/ admin/ settings/   — Bereiche der Oberfläche
│   ├── migrations/         — Datenbank-Migrationen (Alembic)
│   └── tests/              — pytest
└── gottesdienst_formatter_final.py   — Kommandozeile: Excel → Text
```

**Worauf es beim Bauen ankommt:**
- **Das Format ist der Vertrag.** Ein Referenztest
  (`web/tests/test_boyens_goldstandard.py`) vergleicht die Ausgabe mit einer
  freigegebenen Fassung; jede Änderung an den Regeln muss ihn bestehen.
- **Tokens gehören in die Datenbank, nicht in den Code.**
- **Datenbank nur über Migrationen ändern.**

Tests und Stylesheet:

```bash
cd web && pip install -r requirements-dev.txt && pytest
cd .. && npm install && npm run tw:build
```

## Mitmachen

Fehlermeldungen und Vorschläge sind willkommen — gern als
[Issue](https://github.com/Revisor01/gottesdienst-formatter/issues).
Sicherheitslücken bitte vertraulich melden, wie in [SECURITY.md](SECURITY.md)
beschrieben. Pull Requests laufen durch Tests und einen Secret-Scan; die
Grundsätze für Beiträge stehen in [CLAUDE.md](CLAUDE.md).

## Lizenz

Gottesdienst-Formatter steht unter der
[GNU Affero General Public License v3.0](LICENSE). Wer Gottesdienst-Formatter verändert und
anderen zur Verfügung stellt, auch als Webdienst, legt seinen Quelltext unter
derselben Lizenz offen. Wer das nicht möchte, bekommt auf Anfrage eine
kommerzielle Lizenz ([mail@simonluthe.de](mailto:mail@simonluthe.de)). Für
Beiträge gilt [CONTRIBUTING.md](CONTRIBUTING.md).

## Hinweis

Der Gottesdienst-Formatter ist kein Produkt von ChurchDesk oder Boyens
Medien und wird von keinem der beiden Unternehmen unterstützt.

## Kontakt

Pastor Simon Luthe · [mail@simonluthe.de](mailto:mail@simonluthe.de) ·
[simonluthe.de](https://simonluthe.de)
