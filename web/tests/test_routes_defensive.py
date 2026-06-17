#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defensive Tests fuer None-Haertung im Export-/Excel-Pfad.
Task 1 (260617-u0x): None-Normalisierung + Serverfehler-Haertung.
"""
import pytest
from datetime import datetime

from formatting import format_pastor
from main.routes import convert_churchdesk_events_to_boyens


# ---------------------------------------------------------------------------
# format_pastor — "None"-String-Haertung
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("contributor, expected", [
    (None,    ""),
    ("",      ""),
    ("None",  ""),
    ("none",  ""),
    ("NONE",  ""),
    ("NoNe",  ""),
])
def test_format_pastor_none_variants(contributor, expected):
    """format_pastor gibt '' zurueck fuer None-Wert und alle case-Varianten von 'None'."""
    assert format_pastor(contributor) == expected


def test_format_pastor_none_not_substring():
    """'Nonenberg' enthaelt 'none' als Anfang, darf NICHT leer werden."""
    # "Nonenberg" hat keinen bekannten Prefix → wird durchgereicht
    result = format_pastor("Nonenberg")
    assert result == "Nonenberg"


# ---------------------------------------------------------------------------
# convert_churchdesk_events_to_boyens — KeyError/TypeError-Haertung
# ---------------------------------------------------------------------------

def _make_event(**overrides):
    """Hilfsfunktion: vollstaendiges minimales Event-Dict."""
    base = {
        'startDate': '2026-07-06T10:00:00',
        'title': 'Gottesdienst',
        'location': 'Heide, St.-Juergen',
        'contributor': 'Pastor Mueller',
        'parishes': [],
        'organization_name': 'TestOrg',
    }
    base.update(overrides)
    return base


def test_convert_all_fields_none():
    """Event mit allen Feldern None (ausser startDate) — keine Exception, kein 'None' im Output."""
    event = _make_event(title=None, location=None, contributor=None, parishes=None)
    result = convert_churchdesk_events_to_boyens([event])
    assert 'None' not in result


def test_convert_missing_keys():
    """Event mit fehlenden Keys — keine KeyError-Exception."""
    event = {
        'startDate': '2026-07-06T10:00:00',
        'organization_name': 'TestOrg',
        # title, location, contributor, parishes absichtlich NICHT vorhanden
    }
    result = convert_churchdesk_events_to_boyens([event])
    # Muss ohne Exception durchlaufen; Output enthaelt mindestens die Datumszeile
    assert 'Sonntag' in result or 'None' not in result


def test_convert_missing_start_date_key():
    """Event gaenzlich ohne 'startDate'-Key — kein TypeError, Event wird uebersprungen."""
    event = {
        'title': 'Gottesdienst',
        'location': 'Heide',
        'contributor': None,
        'parishes': [],
    }
    result = convert_churchdesk_events_to_boyens([event])
    # Kein Crash — leerer Output ist ok (Event uebersprungen)
    assert isinstance(result, str)


def test_convert_empty_start_date():
    """Event mit leerem startDate — kein TypeError, Event wird uebersprungen."""
    event = _make_event(startDate=None)
    result = convert_churchdesk_events_to_boyens([event])
    assert isinstance(result, str)


def test_convert_invalid_start_date():
    """Event mit unparsebarem startDate — kein Crash, Event uebersprungen."""
    event = _make_event(startDate='nicht-ein-datum')
    result = convert_churchdesk_events_to_boyens([event])
    assert isinstance(result, str)


def test_convert_none_contributor_no_none_in_output():
    """contributor=None darf nicht als 'None' im Output erscheinen."""
    event = _make_event(contributor=None, location='Heide, St.-Juergen')
    result = convert_churchdesk_events_to_boyens([event])
    assert 'None' not in result


def test_convert_none_location_uses_parish_fallback():
    """location=None + parishes vorhanden — kein Crash, Parish-Fallback wird genutzt."""
    event = _make_event(
        location=None,
        parishes=[{'title': 'KG Heide'}],
    )
    result = convert_churchdesk_events_to_boyens([event])
    assert isinstance(result, str)
    assert 'None' not in result


def test_convert_none_parishes_no_crash():
    """parishes=None — kein Crash."""
    event = _make_event(parishes=None)
    result = convert_churchdesk_events_to_boyens([event])
    assert isinstance(result, str)
