<h1 align="center">Gottesdienst-Formatter</h1>

<p align="center">
  Church service dates from ChurchDesk or Excel as ready-to-print text<br>
  for the service listings page of the local daily paper — no rework.
</p>

<p align="center">
  <a href="README.md">Deutsch</a> · <b>English</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776ab?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-SQLite-000000?logo=flask" alt="Flask">
  <img src="https://img.shields.io/github/license/Revisor01/gottesdienst-formatter" alt="License">
</p>

## What it is about

Every month the newspapers of Boyens Medien print the church services in the
Dithmarschen church district — as running text in a precisely defined format.
The dates live in ChurchDesk, spread across many parishes. Copying and
shortening them by hand takes hours and introduces mistakes.

The Gottesdienst-Formatter (“church service formatter”) fetches the dates
itself, brings them into the required format and, if you want, sends the
monthly listing to the editorial office. The tool and its output are German.

## Features

- **ChurchDesk integration** — dates straight from the ChurchDesk API, across
  several organisations (parish groups, parishes)
- **Excel import** — alternatively upload an `.xlsx` file
- **Formatting to spec** — grouped by date, German weekdays and months,
  abbreviations (`Gd.`, `Gd. m. A.`, `P.`, `Pn.`), church name only where a
  village has several churches
- **Administration** — maintain organisations, pastors, service types and
  location rules in the admin area
- **Monthly dispatch** — the listing is emailed to the editorial office
  automatically
- **Export** — download as `.txt` or copy to the clipboard

This is what the result looks like:

```
Sonntag, 1. Juni:
Albersdorf, St. Remigius Kirche: 9.30 Uhr, Gd., P. Keppel
Büsum, St. Clemens-Kirche: 9.30 Uhr, Gd. m. A., Pn. Verwold
```

### Excel format

| Column | Content | Example |
|--------|---------|---------|
| Startdatum | date and time | 2025-06-01 09:30:00 |
| Titel | service type | Gottesdienst, Abendmahl |
| Standortnamen | church and place | Albersdorf, St. Remigius Kirche |
| Mitwirkender | pastor | Pastor Keppel |
| Gemeinden | parish (fallback if there is no location) | Albersdorf |

For single Excel files there is also a command-line script that needs no
server; see [ANLEITUNG.md](ANLEITUNG.md) (German).

## Versions

What changed when is in [CHANGELOG.md](CHANGELOG.md) (in German, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)). The
[releases](https://github.com/Revisor01/gottesdienst-formatter/releases)
summarise each version.

## Running it yourself

**With Docker.** Every state of `main` is available as a ready-made image at
`ghcr.io/revisor01/gottesdienst-formatter`. The file
[web/docker-compose.prod.yml](web/docker-compose.prod.yml) starts it on
port 5001:

```bash
cd web
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec gottesdienst-formatter flask create-admin admin
```

On start the container runs the database migrations. The database (SQLite)
lives in `web/data/` — keep this directory as a volume, otherwise the database
is empty after every restart. The compose file also starts Watchtower, which
pulls new images by itself.

**Locally for development** (Python 3.11):

```bash
git clone https://github.com/Revisor01/gottesdienst-formatter.git
cd gottesdienst-formatter/web
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
pip install -r requirements.txt
flask db upgrade
flask create-admin admin
python -c "from app import create_app; create_app().run(debug=True)"
```

| Variable | Required | Meaning |
|----------|----------|---------|
| `SECRET_KEY` | yes | Session key; the key for the stored mail credentials is derived from it as well. The app does not start without it; if it changes, the mail credentials have to be entered again |
| `CHURCHDESK_ORG_<ID>_TOKEN` | no | API token per organisation; only read on the first `flask db upgrade`, maintained in the admin area afterwards |
| `FLASK_ENV`, `FLASK_DEBUG` | no | `production` and `false` in operation |

Mail dispatch (SMTP server, recipients, day of the month) is configured in the
web interface.

## Structure

```
gottesdienst-formatter
├── web/
│   ├── app.py              — app factory, create-admin command
│   ├── formatting.py       — rules of the newspaper format
│   ├── churchdesk_api.py   — ChurchDesk client for one or more organisations
│   ├── scheduler.py        — monthly dispatch
│   ├── main/ auth/ admin/ settings/   — areas of the interface
│   ├── migrations/         — database migrations (Alembic)
│   └── tests/              — pytest
└── gottesdienst_formatter_final.py   — command line: Excel → text
```

**What matters when building it:**
- **The format is the contract.** A reference test
  (`web/tests/test_boyens_goldstandard.py`) compares the output with an
  approved version; every change to the rules has to pass it.
- **Tokens belong in the database, not in the code.**
- **Change the database only through migrations.**

Tests and stylesheet:

```bash
cd web && pip install -r requirements-dev.txt && pytest
cd .. && npm install && npm run tw:build
```

## Contributing

Bug reports and suggestions are welcome as an
[issue](https://github.com/Revisor01/gottesdienst-formatter/issues). Please
report security issues privately as described in [SECURITY.md](SECURITY.md).
Pull requests go through tests and a secret scan; see
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

Gottesdienst-Formatter is licensed under the
[GNU Affero General Public License v3.0](LICENSE). If you modify it and make
it available to others, including as a web service, you publish your source
code under the same license. The [LICENSE](LICENSE) file is authoritative;
contributions follow [CONTRIBUTING.md](CONTRIBUTING.md).

## Note

Gottesdienst-Formatter is not a product of ChurchDesk or Boyens Medien and is
not supported by either company.

## Contact

Pastor Simon Luthe · [mail@simonluthe.de](mailto:mail@simonluthe.de) ·
[simonluthe.de](https://simonluthe.de)
