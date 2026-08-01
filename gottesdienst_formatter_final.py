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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web'))
from formatting import format_date, format_time, format_service_type, format_pastor

import pandas as pd
from datetime import datetime

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