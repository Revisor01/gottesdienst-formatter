# Kommandozeile: Excel → Text

Wandelt eine Excel-Datei ohne Server in den Fließtext für Boyens Medien um.
Die Spalten der Datei stehen im README unter „Excel-Format“.

```bash
python3 -m venv venv && source venv/bin/activate
pip install pandas openpyxl
python gottesdienst_formatter_final.py
```

Das Skript nimmt die `.xlsx`-Datei im aktuellen Ordner (bei mehreren fragt es
nach) und schreibt das Ergebnis nach `gottesdienste_formatiert.txt`.
