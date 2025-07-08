#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gottesdienst-Formatter Web Interface
Pastor Simon Luthe - Kirchenkreis Dithmarschen
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import os
import tempfile
from datetime import datetime
import io
import zipfile

app = Flask(__name__)
app.secret_key = 'gottesdienst-formatter-secret-key'

def format_date(date_obj):
    """Formatiert Datum im gewünschten Format"""
    if pd.isna(date_obj):
        return ""
    
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
    
    titel_lower = titel.lower()
    
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
    
    name = str(mitwirkender).strip()
    
    prefixes = ['Pastor ', 'Pastorin ', 'P. ', 'Pn. ', 'Diakon ', 'Prädikant ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
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

def process_excel_file(file_path):
    """Verarbeitet Excel-Datei und gibt formatierten Text zurück"""
    try:
        df = pd.read_excel(file_path)
        
        # Validierung der benötigten Spalten
        required_columns = ['Startdatum', 'Titel', 'Standortnamen', 'Mitwirkender', 'Gemeinden']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError("Fehlende Spalten: {}".format(', '.join(missing_columns)))
        
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
                ort = row['Standortnamen'] if not pd.isna(row['Standortnamen']) else row['Gemeinden']
                zeit = format_time(row['Startdatum'])
                gd_typ = format_service_type(row['Titel'])
                pastor = format_pastor(row['Mitwirkender'])
                
                line = "{}: {}, {}".format(ort, zeit, gd_typ)
                if pastor:
                    line += ", {}".format(pastor)
                
                output_lines.append(line)
            
            output_lines.append("")  # Leerzeile nach jedem Tag
        
        return '\n'.join(output_lines), len(df)
    
    except Exception as e:
        raise Exception("Fehler beim Verarbeiten der Excel-Datei: {}".format(str(e)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Keine Datei ausgewählt')
        return redirect(request.url)
    
    if file and file.filename.endswith('.xlsx'):
        try:
            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                file.save(tmp_file.name)
                
                # Verarbeitung
                formatted_text, count = process_excel_file(tmp_file.name)
                
                # Aufräumen
                os.unlink(tmp_file.name)
                
                return render_template('result.html', 
                                     formatted_text=formatted_text, 
                                     count=count)
                
        except Exception as e:
            flash('Fehler beim Verarbeiten der Datei: {}'.format(str(e)))
            return redirect(url_for('index'))
    else:
        flash('Bitte wählen Sie eine Excel-Datei (.xlsx) aus')
        return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def download_file():
    formatted_text = request.form.get('formatted_text')
    if not formatted_text:
        flash('Keine Daten zum Download verfügbar')
        return redirect(url_for('index'))
    
    # Erstelle temporäre Datei
    output = io.StringIO()
    output.write(formatted_text)
    output.seek(0)
    
    # Konvertiere zu BytesIO für Flask
    mem_file = io.BytesIO()
    mem_file.write(output.getvalue().encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        as_attachment=True,
        download_name='gottesdienste_formatiert.txt',
        mimetype='text/plain'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)