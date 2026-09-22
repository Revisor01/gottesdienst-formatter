# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier dokumentiert.

Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionierung folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.1.1] - 2026-09-22

### Behoben

- **Keine Gottesdienste mehr abrufbar**: Die Abfrage an ChurchDesk wurde für
  alle Organisationen abgewiesen, die Übersicht blieb für jeden Monat leer.
  Ursache war das Datumsformat der Anfrage, das ChurchDesk nicht mehr
  akzeptiert. Termine werden wieder wie gewohnt geladen.

### Sicherheit

- Verschlüsselungsbibliothek auf eine gepatchte Version angehoben (behebt ein
  als hoch eingestuftes Finding). Die gespeicherten SMTP-Zugangsdaten bleiben
  unverändert lesbar.
- Zwei Schwachstellen in Build-Werkzeugen behoben; die Oberfläche ist davon
  nicht betroffen.

## [1.1.0] - 2026-08-01

### Geändert

- Abhängigkeiten auf gepatchte Versionen angehoben: Flask 3.1.3, Werkzeug 3.1.6,
  requests 2.33.0, gunicorn 23.0.0, cryptography 48.0.1 — behebt 20 Dependabot-Alerts
  (7 hoch, 13 mittel/niedrig). Testsuite (153 Tests) läuft unverändert grün.
- npm-Abhängigkeiten aktualisiert (postcss, picomatch) — 0 verbleibende Findings

### Behoben

- **Open Redirect beim Login**: Der `next`-Parameter akzeptierte protokoll-relative
  URLs (`//fremder-host`), die Browser als externe Adresse auflösen. Jetzt werden
  nur projekt-interne Pfade übernommen.
- **Stack-Trace-Preisgabe** im SMTP-Test: Exception-Texte gingen an den Client;
  Details landen jetzt im Log, der Client erhält eine generische Meldung.
- Debug-Modus im `__main__`-Block ist opt-in über `FLASK_DEBUG` und bindet auf
  `127.0.0.1` statt auf allen Interfaces

### Sicherheit

- `permissions: contents: read` im CI/CD-Workflow (Least Privilege)

## [1.0.0] - 2026-08-01

Erster Release nach vollständigem Neuaufbau der Git-Historie. Die bisherige
Historie wurde verworfen, weil ChurchDesk-API-Tokens in Commits eines
öffentlichen Repositories lagen (siehe „Sicherheit").

### Hinzugefügt

- **ChurchDesk-Anbindung** — Termine über die ChurchDesk-API v3.0.0 abrufen,
  organisationsübergreifend (Kirchspiele und einzelne Kirchengemeinden)
- **Excel-Import** — Verarbeitung von .xlsx-Dateien mit Gottesdienstdaten
- **Boyens-Formatierung** — Datumsgruppierung, deutsche Wochentage und Monate,
  Abkürzungen (`Gd.`, `Gd. m. A.`, `Gd. m. T.`, `P.`, `Pn.`), Zeitformat „9.30 Uhr"
- **Orts-Regeln** — konfigurierbare Zuordnung von Standorten zu Ausgabe-Orten,
  inklusive Sonderbehandlung für Orte mit mehreren Kirchen
- **Benutzerverwaltung** — Login über Flask-Login, Admin-Rolle, Remember-Me (30 Tage)
- **Admin-Oberfläche** — Pflege von Organisationen, Personen, Gottesdiensttypen,
  Orts-Regeln und Benutzern
- **Automatischer Mailversand** — Scheduler für den monatlichen Redaktionsversand,
  Zugangsdaten verschlüsselt gespeichert
- **Export** — Download als .txt und Copy-to-Clipboard
- **Standalone-CLI** — `gottesdienst_formatter_final.py` für den Excel-Weg ohne Web-UI
- **Testsuite** — pytest inklusive Goldstandard-Test gegen eine Referenz-Ausgabe
- **Docker-Deployment** — docker-compose mit persistentem Volume für die SQLite-Datenbank

### Sicherheit

- ChurchDesk-API-Tokens vollständig aus dem Repository entfernt; die Seed-Migrationen
  beziehen Tokens jetzt aus `CHURCHDESK_ORG_<ID>_TOKEN` und überspringen
  Organisationen ohne gesetzten Token
- Git-Historie neu aufgesetzt, um die zuvor committeten Tokens zu entfernen
- `SECRET_KEY` ist verpflichtend — die Anwendung startet ohne ihn nicht und
  verwendet bewusst keinen generierten Fallback
- `.gitignore` um `.env`, `web/data/`, `web/uploads/` und Planungsartefakte ergänzt
- Dependabot-Alerts, automatische Security-Updates und CodeQL-Code-Scanning aktiviert

[1.1.0]: https://github.com/Revisor01/gottesdienst-formatter/releases/tag/v1.1.0
[1.0.0]: https://github.com/Revisor01/gottesdienst-formatter/releases/tag/v1.0.0
