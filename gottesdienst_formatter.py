#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gottesdienst-Formatter für Boyens Medien
Konvertiert Excel-Tabelle in das gewünschte Fließtext-Format
"""

import pandas as pd
import sys
from datetime import datetime
import locale

# Deutsche Lokalisierung für Wochentage
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE')
    except locale.Error:
        print("Warnung: Deutsche Lokalisierung nicht verfügbar")

def format_date(date_obj):
    """Formatiert Datum im gewünschten Format (z.B. 'Sonnabend, 5. April')"""
    if pd.isna(date_obj):
        return ""
    
    # Wochentag auf Deutsch
    weekday_map = {
        'Monday': 'Montag',
        'Tuesday': 'Dienstag', 
        'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag',
        'Friday': 'Freitag',
        'Saturday': 'Sonnabend',
        'Sunday': 'Sonntag'
    }
    
    weekday = weekday_map.get(date_obj.strftime('%A'), date_obj.strftime('%A'))
    day = date_obj.day
    month_map = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
        5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    month = month_map.get(date_obj.month, date_obj.strftime('%B'))
    
    return "{}, {}. {}".format(weekday, day, month)

def format_time(time_obj):
    """Formatiert Uhrzeit im gewünschten Format"""
    if pd.isna(time_obj):
        return ""
    
    if isinstance(time_obj, str):
        return time_obj
    
    try:
        if hasattr(time_obj, 'hour'):
            hour = time_obj.hour
            minute = time_obj.minute
            if minute == 0:
                return "{} Uhr".format(hour)
            else:
                return "{}.{:02d} Uhr".format(hour, minute)
        else:
            return str(time_obj)
    except:
        return str(time_obj)

def main():
    try:
        # Excel-Datei einlesen
        file_path = "2025-05-20 Gottesdienste 06[1].xlsx"
        
        # Versuche verschiedene Sheet-Namen
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            print("Fehler beim Einlesen der Excel-Datei: {}".format(e))
            return
        
        print("Spalten in der Excel-Datei:")
        print(df.columns.tolist())
        print("\nErste 3 Zeilen der Daten:")
        print(df.head(3))
        
        # Hier würde die eigentliche Formatierung stattfinden
        # Ich erstelle erst mal eine Analyse der Datenstruktur
        
        print("\nDatentypen:")
        print(df.dtypes)
        
        print("\nAnzahl Zeilen:", len(df))
        
        # Suche nach Datum/Zeit-Spalten
        date_columns = []
        time_columns = []
        
        for col in df.columns:
            if any(word in col.lower() for word in ['datum', 'date', 'tag']):
                date_columns.append(col)
            if any(word in col.lower() for word in ['zeit', 'time', 'uhr']):
                time_columns.append(col)
        
        print("\nMögliche Datumsspalten: {}".format(date_columns))
        print("Mögliche Zeitspalten: {}".format(time_columns))
        
    except Exception as e:
        print("Fehler: {}".format(e))
        return

if __name__ == "__main__":
    main()