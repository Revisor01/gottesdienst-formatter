#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests fuer den ChurchDesk-API-Client — insbesondere das Datumsformat.

ChurchDesk validiert startDate/endDate seit 09/2026 strikt (Zod-Schema):
akzeptiert wird entweder ein reines Datum (2026-09-01) oder ein
ISO-Datetime MIT Zeitzone (2026-09-01T00:00:00Z). Ein naives
isoformat() ohne Zeitzone liefert 400 Bad Request.
"""

import re
from datetime import datetime
from unittest.mock import patch

import pytest

from churchdesk_api import ChurchDeskAPI


# Das Zod-Schema der API, auf die relevanten Faelle reduziert:
# reines Datum ODER Datetime mit Zeitzone (Z oder +HH:MM).
DATE_ONLY = re.compile(r'^\d{4}-\d{2}-\d{2}$')
DATETIME_WITH_TZ = re.compile(
    r'^\d{4}-\d{2}-\d{2}T'
    r'(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?'
    r'(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$'
)


def _accepted_by_churchdesk(value: str) -> bool:
    """Bildet die Validierung der ChurchDesk-API nach."""
    return bool(DATE_ONLY.match(value) or DATETIME_WITH_TZ.match(value))


@pytest.fixture
def api():
    return ChurchDeskAPI(api_token='test-token', organization_id=2729)


@pytest.fixture
def captured_params(api):
    """Faengt die Query-Parameter ab, die get_events an die API schicken wuerde."""
    captured = {}

    def fake_request(endpoint, params=None):
        captured.update(params or {})
        return []

    with patch.object(api, '_make_request', side_effect=fake_request):
        api.get_events(
            start_date=datetime(2026, 9, 1),
            end_date=datetime(2026, 9, 30),
        )

    return captured


def test_start_date_wird_von_churchdesk_akzeptiert(captured_params):
    """startDate muss dem Zod-Schema der API genuegen (sonst 400)."""
    start_date = captured_params['startDate']
    assert _accepted_by_churchdesk(start_date), (
        "startDate '{0}' wird von der ChurchDesk-API mit 400 abgelehnt".format(start_date)
    )


def test_end_date_wird_von_churchdesk_akzeptiert(captured_params):
    """endDate muss dem Zod-Schema der API genuegen (sonst 400)."""
    end_date = captured_params['endDate']
    assert _accepted_by_churchdesk(end_date), (
        "endDate '{0}' wird von der ChurchDesk-API mit 400 abgelehnt".format(end_date)
    )


def test_datum_bleibt_inhaltlich_erhalten(captured_params):
    """Der Kalendertag darf sich durch die Formatierung nicht verschieben."""
    assert captured_params['startDate'].startswith('2026-09-01')
    assert captured_params['endDate'].startswith('2026-09-30')


def test_naives_isoformat_ist_der_verbotene_fall():
    """Gegenprobe: genau das alte Format loest den 400er aus."""
    assert not _accepted_by_churchdesk('2026-09-01T00:00:00')


def test_erlaubte_formate_gelten_als_gueltig():
    """Gegenprobe: die von der API dokumentierten Formate sind erlaubt."""
    assert _accepted_by_churchdesk('2026-09-01')
    assert _accepted_by_churchdesk('2026-09-01T00:00:00Z')
    assert _accepted_by_churchdesk('2026-09-01T00:00:00+02:00')


def test_zeitzonenbehaftetes_datum_bleibt_gueltig(api):
    """Ein datetime mit tzinfo darf ebenfalls kein ungueltiges Format erzeugen."""
    import pytz

    captured = {}

    def fake_request(endpoint, params=None):
        captured.update(params or {})
        return []

    berlin = pytz.timezone('Europe/Berlin')
    with patch.object(api, '_make_request', side_effect=fake_request):
        api.get_events(
            start_date=berlin.localize(datetime(2026, 9, 1, 8, 30)),
            end_date=berlin.localize(datetime(2026, 9, 30, 20, 0)),
        )

    assert _accepted_by_churchdesk(captured['startDate'])
    assert _accepted_by_churchdesk(captured['endDate'])
