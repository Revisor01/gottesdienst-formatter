#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gottesdienst-Formatter für Boyens Medien
Konvertiert Excel-Tabelle in das gewünschte Fließtext-Format

Verwendung:
1. Excel-Datei in den gleichen Ordner wie dieses Script legen
2. Script ausführen: python gottesdienst_formatter_final.py
3. Ergebnis wird in 'gottesdienste_formatiert.txt' gespeichert
"""

import pandas as pd
import sys
from datetime import datetime
import os

def format_date(date_obj):
    """Formatiert Datum im gewünschten Format (z.B. 'Sonnabend, 5. April')"""
    if pd.isna(date_obj):
        return ""
    
    # Wochentag auf Deutsch
    weekday_map = {
        0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag',
        4: 'Freitag', 5: 'Sonnabend', 6: 'Sonntag'
    }
    
    weekday = weekday_map.get(date_obj.weekday(), 'Unbekannt')
    day = date_obj.day
    
    month_map = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
        5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    month = month_map.get(date_obj.month, 'Unbekannt')
    
    return "{}, {}. {}".format(weekday, day, month)

def format_time(date_obj):
    """Extrahiert und formatiert Uhrzeit aus datetime"""
    if pd.isna(date_obj):
        return ""
    
    hour = date_obj.hour
    minute = date_obj.minute
    
    if minute == 0:
        return "{} Uhr".format(hour)
    else:
        return "{}.{:02d} Uhr".format(hour, minute)

def format_service_type(titel):
    """Formatiert den Gottesdiensttyp"""
    if pd.isna(titel):
        return "Gd."
    
    # Mapping für häufige Gottesdiensttypen
    type_map = {
        'gottesdienst': 'Gd.',
        'abendmahl': 'Gd. m. A.',
        'taufe': 'Gd. m. T.',
        'konfirmation': 'Konfirmation',
        'kinderkirche': 'Kinderkirche',
        'familiengottesdienst': 'Familiengd.',
        'andacht': 'Andacht'
    }
    
    titel_lower = titel.lower()
    
    # Spezielle Behandlung für verschiedene Gottesdiensttypen
    if 'abendmahl' in titel_lower:
        return 'Gd. m. A.'
    elif 'taufe' in titel_lower:
        return 'Gd. m. T.'
    elif 'konfirmation' in titel_lower:
        return 'Konfirmation'
    elif 'kinderkirche' in titel_lower or 'kinder' in titel_lower:
        return 'Kinderkirche'
    elif 'familie' in titel_lower:
        return 'Familiengd.'
    elif 'andacht' in titel_lower:
        return 'Andacht'
    else:
        return 'Gd.'

def format_pastor(mitwirkender):
    """Formatiert Pastor/Pastorin Namen"""
    if pd.isna(mitwirkender):
        return ""
    
    # Bereinige den Namen
    name = str(mitwirkender).strip()
    
    # Entferne häufige Präfixe falls vorhanden
    prefixes = ['Pastor ', 'Pastorin ', 'P. ', 'Pn. ', 'Diakon ', 'Prädikant ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Füge korrektes Präfix hinzu basierend auf Geschlecht (vereinfacht)
    # Hier könnte eine erweiterte Logik implementiert werden
    if any(word in mitwirkender.lower() for word in ['pastorin', 'pn.']):
        return "Pn. {}".format(name)
    elif any(word in mitwirkender.lower() for word in ['pastor', 'p.']):
        return "P. {}".format(name)
    elif 'diakon' in mitwirkender.lower():
        return "Diakon {}".format(name)
    elif 'prädikant' in mitwirkender.lower():
        return "Prädikant {}".format(name)
    else:
        return "P. {}".format(name)

def main():
    try:
        # Suche nach Excel-Dateien im aktuellen Verzeichnis
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if not excel_files:
            print("Keine Excel-Dateien gefunden!")
            return
        
        if len(excel_files) == 1:
            file_path = excel_files[0]
        else:
            print("Mehrere Excel-Dateien gefunden:")
            for i, file in enumerate(excel_files, 1):
                print("{}. {}".format(i, file))
            
            try:
                choice = int(input("Welche Datei soll verwendet werden? (Nummer eingeben): ")) - 1
                file_path = excel_files[choice]
            except (ValueError, IndexError):
                print("Ungültige Auswahl!")
                return
        
        print("Verwende Datei: {}".format(file_path))
        
        # Excel-Datei einlesen
        df = pd.read_excel(file_path)
        
        # Daten nach Datum sortieren
        df = df.sort_values('Startdatum')
        
        # Gruppiere nach Datum
        grouped = df.groupby(df['Startdatum'].dt.date)
        
        output_lines = []
        
        for date, group in grouped:
            # Datum formatieren
            date_str = format_date(pd.to_datetime(date))
            output_lines.append("{}:".format(date_str))
            
            # Termine für diesen Tag
            for _, row in group.iterrows():
                # Zeile formatieren: Ort: Zeit, Gottesdiensttyp, Pastor
                ort = row['Standortnamen'] if not pd.isna(row['Standortnamen']) else row['Gemeinden']
                zeit = format_time(row['Startdatum'])
                gd_typ = format_service_type(row['Titel'])
                pastor = format_pastor(row['Mitwirkender'])
                
                # Zeile zusammenbauen
                line = "{}: {}, {}".format(ort, zeit, gd_typ)
                if pastor:
                    line += ", {}".format(pastor)
                
                output_lines.append(line)
            
            output_lines.append("")  # Leerzeile nach jedem Tag
        
        # Ergebnis in Datei schreiben
        output_file = 'gottesdienste_formatiert.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print("Formatierung abgeschlossen!")
        print("Ergebnis gespeichert in: {}".format(output_file))
        
        # Vorschau anzeigen
        print("\n--- VORSCHAU ---")
        for line in output_lines[:20]:  # Erste 20 Zeilen
            print(line)
        
        if len(output_lines) > 20:
            print("... (weitere {} Zeilen in der Datei)".format(len(output_lines) - 20))
        
    except Exception as e:
        print("Fehler: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()