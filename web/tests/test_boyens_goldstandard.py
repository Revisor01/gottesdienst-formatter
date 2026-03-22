#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End-Goldstandard-Test: Statische Eingabedaten werden durch die
Formatierungspipeline geschickt und mit dem erwarteten Boyens-Output verglichen.
"""
import json
import os
from datetime import datetime

import pytest

from formatting import format_date, format_time, format_service_type, format_pastor
from main.routes import _build_location_entries, _extract_suffix


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def load_fixture_input():
    with open(os.path.join(FIXTURES_DIR, 'boyens_reference_input.json'), encoding='utf-8') as f:
        return json.load(f)


def load_fixture_output():
    with open(os.path.join(FIXTURES_DIR, 'boyens_reference_output.txt'), encoding='utf-8') as f:
        return f.read()


def build_boyens_text_from_fixture(events):
    """
    Konvertiert die strukturierten Fixture-Events in Boyens-Fliesstext.
    Repliziert die Logik aus app.convert_churchdesk_events_to_boyens.
    """
    # Gruppiere nach Datum
    events_by_date = {}
    for evt in events:
        date_obj = datetime.strptime(evt['date'], '%Y-%m-%d')
        date_key = date_obj.date()
        dt = date_obj.replace(hour=evt['time_hour'], minute=evt['time_minute'])
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append({
            'startDate': dt,
            'location': evt['location'],
            'title': evt['title'],
            'contributor': evt['contributor'],
        })

    output_lines = []
    for date in sorted(events_by_date.keys()):
        date_obj = datetime.combine(date, datetime.min.time())
        output_lines.append("{}:".format(format_date(date_obj)))

        day_events = sorted(events_by_date[date], key=lambda x: x['startDate'])
        day_items = []
        for evt in day_events:
            titel = evt['title'] or ''
            day_items.append({
                'location': evt['location'],
                'time_str': format_time(evt['startDate']),
                'service_type': format_service_type(titel),
                'pastor': format_pastor(evt['contributor']),
                'suffix': _extract_suffix(titel),
            })

        output_lines.extend(_build_location_entries(day_items))
        output_lines.append('')  # Leerzeile nach jedem Tag

    return '\n'.join(output_lines)


def test_goldstandard_output_matches_reference():
    """Gesamter Output muss exakt der Referenzdatei entsprechen."""
    events = load_fixture_input()
    actual = build_boyens_text_from_fixture(events)
    expected = load_fixture_output()
    assert actual == expected, (
        "Goldstandard-Abweichung!\n"
        "=== ERWARTET ===\n{}\n"
        "=== ERHALTEN ===\n{}\n".format(expected, actual)
    )


def test_goldstandard_line_by_line():
    """Zeilenweiser Vergleich fuer bessere Fehlermeldungen."""
    events = load_fixture_input()
    actual = build_boyens_text_from_fixture(events)
    expected = load_fixture_output()

    actual_lines = actual.split('\n')
    expected_lines = expected.split('\n')

    for i, (act_line, exp_line) in enumerate(zip(actual_lines, expected_lines), start=1):
        assert act_line == exp_line, (
            "Zeile {}: erwartet {!r}, erhalten {!r}".format(i, exp_line, act_line)
        )

    assert len(actual_lines) == len(expected_lines), (
        "Zeilenanzahl: erwartet {}, erhalten {}".format(
            len(expected_lines), len(actual_lines)
        )
    )
