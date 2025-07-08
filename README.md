# Gottesdienst-Formatter für Boyens Medien

Ein Tool zur automatischen Konvertierung von Excel-Tabellen mit Gottesdienstdaten in das von Boyens Medien geforderte Fließtext-Format.

## Über das Projekt

Entwickelt für den Kirchenkreis Dithmarschen zur Vereinfachung der Übermittlung von Gottesdienstterminen an Boyens Medien. Das Tool konvertiert strukturierte Excel-Daten automatisch in das korrekte Format für die Veröffentlichung.

## Features

- **Web-Interface**: Einfacher Upload von Excel-Dateien
- **Automatische Formatierung**: Konvertierung in Boyens Medien Format
- **Sortierung**: Termine automatisch nach Datum gruppiert
- **Export**: Download als .txt-Datei oder Copy-to-Clipboard
- **Responsive Design**: Funktioniert auf Desktop und Mobile
- **Docker-basiert**: Einfaches Deployment

## Projektstruktur

```
├── web/                    # Web-Anwendung
│   ├── app.py             # Flask-Hauptanwendung
│   ├── templates/         # HTML-Templates
│   │   ├── base.html      # Basis-Template
│   │   ├── index.html     # Startseite
│   │   └── result.html    # Ergebnisseite
│   ├── requirements.txt   # Python-Abhängigkeiten
│   ├── Dockerfile         # Docker-Konfiguration
│   └── docker-compose.yml # Docker Compose Setup
├── gottesdienst_formatter_final.py  # Standalone-Script
└── ANLEITUNG.md          # Detaillierte Anleitung
```

## Schnellstart

### 1. Repository klonen
```bash
git clone <repository-url>
cd gottesdienst-formatter
```

### 2. Web-Anwendung starten
```bash
cd web
docker compose up -d
```

Die Anwendung ist dann erreichbar unter http://localhost:5001

### 3. Standalone-Script nutzen
```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas openpyxl
python gottesdienst_formatter_final.py
```

## Excel-Datenformat

Die Excel-Datei muss folgende Spalten enthalten:

| Spalte | Beschreibung | Beispiel |
|--------|-------------|----------|
| Startdatum | Datum und Uhrzeit | 2025-06-01 09:30:00 |
| Titel | Gottesdiensttyp | Gottesdienst, Abendmahl, etc. |
| Standortnamen | Kirche/Ort | Albersdorf, St. Remigius Kirche |
| Mitwirkender | Pastor/Pastorin | Pastor Keppel |
| Gemeinden | Gemeinde (Fallback) | Albersdorf |

## Ausgabeformat

Das Tool erstellt automatisch das korrekte Format:

```
Sonntag, 1. Juni:
Albersdorf, St. Remigius Kirche: 9.30 Uhr, Gd., P. Keppel
Büsum, St. Clemens-Kirche: 9.30 Uhr, Gd. m. A., Pn. Verwold
```

## Deployment

### Produktionsumgebung mit Caddy

1. **Dateien kopieren:**
```bash
scp -r web root@server:/opt/gottesdienst-formatter/
```

2. **Container starten:**
```bash
cd /opt/gottesdienst-formatter
docker compose up -d
```

3. **Caddy konfigurieren:**
```caddy
gd.example.com {
    reverse_proxy localhost:5001
}
```

4. **Caddy neu laden:**
```bash
systemctl reload caddy
```

## Konfiguration

### Umgebungsvariablen

- `FLASK_ENV`: Produktionsumgebung (`production`)
- `FLASK_DEBUG`: Debug-Modus (`false`)

### Docker-Ports

Standardmäßig läuft die Anwendung auf Port 5001. Kann in `docker-compose.yml` angepasst werden.

## Wartung

### Logs einsehen
```bash
docker logs gottesdienst-formatter
```

### Container neustarten
```bash
docker compose restart
```

### Updates einspielen
```bash
git pull
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Fehlerbehebung

### Häufige Probleme

1. **Port bereits belegt**: Port in `docker-compose.yml` ändern
2. **Excel-Datei nicht erkannt**: Spaltenüberschriften prüfen
3. **Formatierung falsch**: Datum/Zeit-Format in Excel überprüfen

### Debug-Modus aktivieren
```bash
# In docker-compose.yml
environment:
  - FLASK_DEBUG=true
```

## Anforderungen Boyens Medien

- Termine nach Datum sortiert und zusammengefasst
- Format: "Ort: Zeit, Gottesdiensttyp, Pastor"
- Bei mehreren Kirchen pro Ort: Kirchenname angeben
- Keine Tabellen oder zusätzliche Formatierung
- Deadline: bis zum 20. des Vormonats
- E-Mail: redaktion@boyens-medien.de

## Lizenz

© 2025 Pastor Simon Luthe, Kirchenkreis Dithmarschen

Dieses Projekt wurde entwickelt für den internen Gebrauch des Kirchenkreises Dithmarschen.