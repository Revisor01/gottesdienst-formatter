#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Haupt-Routes als Flask Blueprint — alle bestehenden Routes aus app.py.
"""
import json
from datetime import datetime
import io

from flask import render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required

from churchdesk_api import ChurchDeskAPI, EventAnalyzer, create_multi_org_client, extract_boyens_location
from formatting import format_date, format_time, format_service_type, format_pastor
from config import ORGANIZATIONS
from main import bp


@bp.app_template_filter('format_parish')
def format_parish_name(parish_title):
    """Format parish name for display using location mappings"""
    if not parish_title:
        return ""

    # Remove KG prefix if present
    if parish_title.startswith('KG '):
        parish_title = parish_title[3:]

    # Apply location mapping for display (not export)
    return extract_boyens_location(parish_title, for_export=False)


def _extract_suffix(titel):
    """Keine Zusatzinfos im Boyens-Output — strikt nur Typ + Pastor."""
    return ''


def _build_location_entries(day_items):
    """
    Gruppiert Termineintraege nach Ort und wendet jeweils-Logik an (D-20, D-29, D-31).

    day_items: Liste von Dicts mit keys: location, time_str, service_type, pastor, suffix

    Gibt sortierte Liste von Zeilen zurueck: ["Ort: Eintrag1; Eintrag2, jeweils Pn. X", ...]
    """
    location_entries = {}  # {location: [{'time', 'service_type', 'pastor', 'suffix'}]}

    for item in day_items:
        loc = item['location']
        if loc not in location_entries:
            location_entries[loc] = []
        location_entries[loc].append(item)

    lines = []
    for location in sorted(location_entries.keys()):  # D-29: alphabetisch
        entries = location_entries[location]
        pastors = [e['pastor'] for e in entries]

        # D-20 / FMT-08: jeweils-Logik
        if len(entries) > 1 and len(set(pastors)) == 1 and pastors[0]:
            # Alle Eintraege haben denselben Pastor → Pastor einmal am Ende
            entry_strings = []
            for e in entries:
                s = "{}, {}".format(e['time_str'], e['service_type'])
                if e.get('suffix'):
                    s += e['suffix']
                entry_strings.append(s)
            line = "{}: {}, jeweils {}".format(location, '; '.join(entry_strings), pastors[0])
        else:
            # Unterschiedliche Pastoren → Pastor bei jedem Eintrag einzeln
            entry_strings = []
            for e in entries:
                s = "{}, {}".format(e['time_str'], e['service_type'])
                if e.get('suffix'):
                    s += e['suffix']
                if e['pastor']:
                    s += ", {}".format(e['pastor'])
                entry_strings.append(s)
            line = "{}: {}".format(location, '; '.join(entry_strings))  # D-31

        lines.append(line)

    return lines


def convert_churchdesk_events_to_boyens(events):
    """Convert ChurchDesk events to Boyens format with location extraction"""
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
            'parishes': event['parishes'],
            'organization_name': event.get('organization_name', '')
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

        # Sammle Termineintraege fuer diesen Tag
        day_items = []
        for event in day_events:
            # Extract Boyens-conform location for export (Urlauberseelsorge → Buesum)
            location = extract_boyens_location(event['location'], for_export=True)
            if not location and event['parishes']:
                location = extract_boyens_location(event['parishes'][0].get('title', ''), for_export=True)

            titel = event['title'] or ''
            day_items.append({
                'location': location,
                'time_str': format_time(event['startDate']),
                'service_type': format_service_type(titel),
                'pastor': format_pastor(event['contributor']),
                'suffix': _extract_suffix(titel),
            })

        # Alphabetisch sortieren, Multi-Termin zusammenfassen, jeweils-Logik anwenden
        output_lines.extend(_build_location_entries(day_items))
        output_lines.append("")  # Empty line after each date

    return '\n'.join(output_lines)


@bp.route('/health')
def health():
    return {'status': 'ok'}, 200


@bp.route('/')
@login_required
def index():
    current_year = datetime.now().year
    return render_template('index.html', organizations=ORGANIZATIONS,
                           current_year=current_year)


@bp.route('/download', methods=['POST'])
@login_required
def download_file():
    formatted_text = request.form.get('formatted_text')
    if not formatted_text:
        flash('Keine Daten zum Download verfuegbar')
        return redirect(url_for('main.index'))

    # Erstelle temporaere Datei
    output = io.StringIO()
    output.write(formatted_text)
    output.seek(0)

    # Konvertiere zu BytesIO fuer Flask
    mem_file = io.BytesIO()
    mem_file.write(output.getvalue().encode('utf-8'))
    mem_file.seek(0)

    return send_file(
        mem_file,
        as_attachment=True,
        download_name='gottesdienste_formatiert.txt',
        mimetype='text/plain'
    )


@bp.route('/fetch_churchdesk_events', methods=['POST'])
@login_required
def fetch_churchdesk_events():
    """Fetch events from ChurchDesk API for multiple organizations"""
    try:
        # Get form data
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
        selected_orgs = request.form.getlist('selected_organizations')

        if not selected_orgs:
            flash('Bitte waehlen Sie mindestens eine Organisation aus')
            return redirect(url_for('main.index'))

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
            1: 'Januar', 2: 'Februar', 3: 'Maerz', 4: 'April',
            5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }

        # Get organization names for display
        selected_org_names = [ORGANIZATIONS.get(org_id, {}).get('name', 'Org {}'.format(org_id))
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
        return redirect(url_for('main.index'))


@bp.route('/export_selected_events', methods=['POST'])
@login_required
def export_selected_events():
    """Export selected events to Boyens format"""
    try:
        # Get selected events data
        events_data = request.form.get('events_data')
        selected_event_ids = request.form.getlist('selected_events')

        if not events_data or not selected_event_ids:
            flash('Keine Events ausgewaehlt')
            return redirect(url_for('main.index'))

        # Parse events data
        events = json.loads(events_data)

        # Filter selected events
        selected_events = [e for e in events if str(e['id']) in selected_event_ids]

        if not selected_events:
            flash('Keine gueltigen Events ausgewaehlt')
            return redirect(url_for('main.index'))

        # Convert to Boyens format
        formatted_text = convert_churchdesk_events_to_boyens(selected_events)

        return render_template('result.html',
                               formatted_text=formatted_text,
                               count=len(selected_events),
                               source='ChurchDesk')

    except Exception as e:
        flash('Fehler beim Exportieren der Events: {}'.format(str(e)))
        return redirect(url_for('main.index'))
