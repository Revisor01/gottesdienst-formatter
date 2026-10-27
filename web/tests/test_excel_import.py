#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel-Import: die Termine des Boyens-Fixtures als ChurchDesk-Export (xlsx)
durch process_excel_file. Sichert die pandas-Pfade (read_excel, .dt.date,
isna) gegen Versionswechsel ab; Erwartung aufgenommen mit pandas 2.3.1.
Der Export-Pfad hängt an Orte ohne Kirchennamen ", Kirche" an.
"""
import json
import os
from datetime import datetime

import pytest
from openpyxl import Workbook

from main.routes import process_excel_file


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
SPALTEN = ['Startdatum', 'Titel', 'Standortnamen', 'Mitwirkender', 'Gemeinden']


def schreibe_xlsx(pfad, zeilen):
    wb = Workbook()
    ws = wb.active
    ws.append(SPALTEN)
    for zeile in zeilen:
        ws.append([zeile.get(s) for s in SPALTEN])
    wb.save(pfad)


def fixture_zeilen():
    with open(os.path.join(FIXTURES_DIR, 'boyens_reference_input.json'), encoding='utf-8') as f:
        events = json.load(f)
    zeilen = []
    for evt in events:
        datum = datetime.strptime(evt['date'], '%Y-%m-%d').replace(
            hour=evt['time_hour'], minute=evt['time_minute'])
        zeilen.append({
            'Startdatum': datum,
            'Titel': evt['title'],
            'Standortnamen': evt['location'],
            'Mitwirkender': evt['contributor'],
            'Gemeinden': None,
        })
    return zeilen


def test_excel_import_fixture_termine(tmp_path):
    pfad = tmp_path / 'export.xlsx'
    zeilen = fixture_zeilen()
    schreibe_xlsx(pfad, zeilen)

    text, anzahl = process_excel_file(str(pfad))

    assert anzahl == 4
    assert text == (
        'Sonntag, 6. April:\n'
        'Heide, St.-Jürgen: 10 Uhr, Gd., P. Mueller; 11 Uhr, Kinderkirche, Pn. Schmidt\n'
        'Meldorf, Kirche: 10 Uhr, Gd. m. A., Pn. Schmidt\n'
        '\n'
        'Sonntag, 13. April:\n'
        'Wesselburen, Kirche: 9.30 Uhr, Familiengd., Diakon Weber\n'
    )


def test_excel_import_leere_zellen(tmp_path):
    """Leerer Standort fällt auf die Gemeinde zurück, leerer Mitwirkender bleibt leer."""
    pfad = tmp_path / 'export.xlsx'
    schreibe_xlsx(pfad, [
        {'Startdatum': datetime(2025, 4, 6, 10, 0), 'Titel': 'Gottesdienst',
         'Standortnamen': None, 'Mitwirkender': 'Pastor Mueller', 'Gemeinden': 'Meldorf'},
        {'Startdatum': datetime(2025, 4, 6, 18, 0), 'Titel': 'Gottesdienst',
         'Standortnamen': 'Wesselburen', 'Mitwirkender': None, 'Gemeinden': None},
    ])

    text, anzahl = process_excel_file(str(pfad))

    assert anzahl == 2
    assert text.strip() == (
        'Sonntag, 6. April:\n'
        'Meldorf, Kirche: 10 Uhr, Gd., P. Mueller\n'
        'Wesselburen, Kirche: 18 Uhr, Gd.'
    )


def test_excel_import_fehlende_spalte(tmp_path):
    pfad = tmp_path / 'export.xlsx'
    wb = Workbook()
    wb.active.append(['Startdatum', 'Titel'])
    wb.save(pfad)

    with pytest.raises(Exception, match='Fehlende Spalten: Standortnamen, Mitwirkender, Gemeinden'):
        process_excel_file(str(pfad))
