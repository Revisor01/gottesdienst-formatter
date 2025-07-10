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
import json
from churchdesk_api import ChurchDeskAPI, EventAnalyzer, create_multi_org_client, ORGANIZATIONS

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


@app.route('/fetch_churchdesk_events', methods=['POST'])
def fetch_churchdesk_events():
    """Fetch events from ChurchDesk API for multiple organizations"""
    try:
        # Get form data
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
        selected_orgs = request.form.getlist('selected_organizations')
        
        if not selected_orgs:
            flash('Bitte wählen Sie mindestens eine Organisation aus')
            return redirect(url_for('index'))
        
        # Convert to integers
        selected_org_ids = [int(org_id) for org_id in selected_orgs]
        
        # Create multi-organization API client
        multi_client = create_multi_org_client(selected_org_ids)
        
        # Fetch events for the specified month from all selected organizations
        events = multi_client.get_monthly_events(year, month, gottesdienst_only=True)
        
        # Process events for display
        processed_events = []
        for event in events:
            formatted_event = EventAnalyzer.format_event_for_boyens(event)
            if formatted_event:
                # Add formatted date/time for display
                formatted_event['formatted_date'] = format_date(formatted_event['startDate'])
                formatted_event['formatted_time'] = format_time(formatted_event['startDate'])
                
                # Add organization info
                formatted_event['organization_name'] = event.get('organization_name', 'Unbekannt')
                formatted_event['organization_id'] = event.get('organization_id', 0)
                
                processed_events.append(formatted_event)
        
        # Sort by date
        processed_events.sort(key=lambda x: x['startDate'])
        
        # Month names for display
        month_names = {
            1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
            5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }
        
        # Get organization names for display
        selected_org_names = [ORGANIZATIONS.get(org_id, {}).get('name', f'Org {org_id}') 
                             for org_id in selected_org_ids]
        
        return render_template('churchdesk_events.html', 
                             events=processed_events,
                             events_json=json.dumps([{
                                 'id': e['id'],
                                 'title': e['title'],
                                 'startDate': e['startDate'].isoformat(),
                                 'location': e['location'],
                                 'contributor': e['contributor'],
                                 'parishes': e['parishes'],
                                 'organization_id': e.get('organization_id', 0),
                                 'organization_name': e.get('organization_name', 'Unbekannt')
                             } for e in processed_events]),
                             year=year,
                             month=month,
                             month_name=month_names[month],
                             selected_organizations=selected_org_names)
        
    except Exception as e:
        flash('Fehler beim Abrufen der ChurchDesk Events: {}'.format(str(e)))
        return redirect(url_for('index'))


@app.route('/export_selected_events', methods=['POST'])
def export_selected_events():
    """Export selected events to Boyens format"""
    try:
        # Get selected events data
        events_data = request.form.get('events_data')
        selected_event_ids = request.form.getlist('selected_events')
        
        if not events_data or not selected_event_ids:
            flash('Keine Events ausgewählt')
            return redirect(url_for('index'))
        
        # Parse events data
        events = json.loads(events_data)
        
        # Filter selected events
        selected_events = [e for e in events if str(e['id']) in selected_event_ids]
        
        if not selected_events:
            flash('Keine gültigen Events ausgewählt')
            return redirect(url_for('index'))
        
        # Convert to Boyens format
        formatted_text = convert_churchdesk_events_to_boyens(selected_events)
        
        return render_template('result.html', 
                             formatted_text=formatted_text, 
                             count=len(selected_events),
                             source='ChurchDesk')
        
    except Exception as e:
        flash('Fehler beim Exportieren der Events: {}'.format(str(e)))
        return redirect(url_for('index'))


def convert_churchdesk_events_to_boyens(events):
    """Convert ChurchDesk events to Boyens format"""
    # Group events by date
    events_by_date = {}
    
    for event in events:
        start_date = datetime.fromisoformat(event['startDate'])
        date_key = start_date.date()
        
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        
        events_by_date[date_key].append({
            'startDate': start_date,
            'title': event['title'],
            'location': event['location'],
            'contributor': event['contributor'],
            'parishes': event['parishes']
        })
    
    # Sort dates
    sorted_dates = sorted(events_by_date.keys())
    
    output_lines = []
    
    for date in sorted_dates:
        # Format date
        date_obj = datetime.combine(date, datetime.min.time())
        date_str = format_date(date_obj)
        output_lines.append("{}:".format(date_str))
        
        # Sort events by time for this date
        day_events = sorted(events_by_date[date], key=lambda x: x['startDate'])
        
        for event in day_events:
            # Format location
            location = event['location']
            if not location and event['parishes']:
                location = event['parishes'][0].get('title', '')
            
            # Format time
            time_str = format_time(event['startDate'])
            
            # Format service type
            service_type = format_service_type(event['title'])
            
            # Format pastor
            pastor = format_pastor(event['contributor'])
            
            # Build line
            line = "{}: {}, {}".format(location, time_str, service_type)
            if pastor:
                line += ", {}".format(pastor)
            
            output_lines.append(line)
        
        output_lines.append("")  # Empty line after each date
    
    return '\n'.join(output_lines)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)