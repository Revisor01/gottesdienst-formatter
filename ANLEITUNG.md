# Gottesdienst-Formatter für Boyens Medien

## Beschreibung
Dieses Script konvertiert Excel-Tabellen mit Gottesdienstdaten automatisch in das von Boyens Medien geforderte Fließtext-Format.

## Vorbereitung (nur einmal nötig)
1. Terminal/Eingabeaufforderung öffnen
2. Zu diesem Ordner navigieren: `cd /Users/simonluthe/Documents/kk-termine`
3. Virtual Environment aktivieren: `source venv/bin/activate`

## Verwendung
1. Excel-Datei mit Gottesdienstdaten in diesen Ordner legen
2. Terminal öffnen und zu diesem Ordner navigieren
3. Virtual Environment aktivieren: `source venv/bin/activate`
4. Script ausführen: `python gottesdienst_formatter_final.py`
5. Bei mehreren Excel-Dateien: gewünschte Datei auswählen
6. Ergebnis wird in `gottesdienste_formatiert.txt` gespeichert

## Ausgabeformat
Das Script erstellt automatisch das korrekte Format:
- Nach Datum sortiert und gruppiert
- Format: "Ort: Zeit, Gottesdiensttyp, Pastor"
- Deutsche Wochentage und Monate
- Keine Tabellen oder zusätzliche Formatierung

## Beispiel-Ausgabe
```
Sonntag, 1. Juni:
Albersdorf, St. Remigius Kirche: 9.30 Uhr, Gd., P. Keppel
Büsum, St. Clemens-Kirche: 9.30 Uhr, Gd. m. A., Pn. Ulrike Verwold
```

## Hinweise
- Das Script erkennt automatisch Gottesdiensttypen (Abendmahl, Taufe, etc.)
- Pastoren-Titel werden automatisch korrekt formatiert
- Bei Problemen: Überprüfen Sie die Spaltenüberschriften in der Excel-Datei