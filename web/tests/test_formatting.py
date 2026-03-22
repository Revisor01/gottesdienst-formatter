#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests fuer alle Formatierungsfunktionen in web/formatting.py.
"""
import pytest
import pandas as pd
from datetime import datetime

from formatting import format_date, format_time, format_service_type, format_pastor
from churchdesk_api import extract_boyens_location


# ---------------------------------------------------------------------------
# format_date
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("date_obj, expected", [
    (datetime(2025, 4, 5),  "Sonnabend, 5. April"),
    (datetime(2025, 4, 6),  "Sonntag, 6. April"),
    (datetime(2025, 12, 25), "Donnerstag, 25. Dezember"),
    (datetime(2025, 1, 1),  "Mittwoch, 1. Januar"),
    (datetime(2025, 5, 19), "Montag, 19. Mai"),
    (datetime(2025, 6, 3),  "Dienstag, 3. Juni"),
    (datetime(2025, 9, 12), "Freitag, 12. September"),
])
def test_format_date(date_obj, expected):
    assert format_date(date_obj) == expected


def test_format_date_nat():
    assert format_date(pd.NaT) == ""


# ---------------------------------------------------------------------------
# format_time
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hour, minute, expected", [
    (9,  30, "9.30 Uhr"),
    (17,  0, "17 Uhr"),
    (10,  0, "10 Uhr"),
    (11, 15, "11.15 Uhr"),
    (8,  45, "8.45 Uhr"),
    (0,   0, "0 Uhr"),
    (18, 30, "18.30 Uhr"),
])
def test_format_time(hour, minute, expected):
    dt = datetime(2025, 4, 6, hour, minute)
    assert format_time(dt) == expected


def test_format_time_nat():
    assert format_time(pd.NaT) == ""


# ---------------------------------------------------------------------------
# format_service_type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("titel, expected", [
    ("Gottesdienst",                        "Gd."),
    ("Abendmahlsgottesdienst",              "Gd. m. A."),
    ("Taufgottesdienst",                    "Gd. m. T."),
    ("Gottesdienst mit Abendmahl und Taufe","Abendmahlgd. m. T."),
    ("Konfirmation",                        "Konfirmation"),
    ("Konfirmandenprüfung",                 "Gd. m. Konfirmandenprüfung"),
    ("Familiengottesdienst",               "Familiengd."),
    ("Gottesdienst mit Popularmusik",       "Gd. m. Popularmusik"),
    ("1. Konfirmation",                     "1. Konfirmation"),
    ("Tauffest",                            "Tauffest"),
    ("Diamantene Konfirmation",             "Diamantene Konfirmation"),
    ("Andacht",                             "Andacht"),
    ("Kinderkirche",                        "Kinderkirche"),
    ("Abendsegen",                          "Abendsegen"),
])
def test_format_service_type(titel, expected):
    assert format_service_type(titel) == expected


def test_format_service_type_nat():
    assert format_service_type(pd.NaT) == "Gd."


def test_format_service_type_case_insensitive():
    # Gross-/Kleinschreibung spielt keine Rolle
    assert format_service_type("GOTTESDIENST") == "Gd."
    assert format_service_type("abendmahlsgottesdienst") == "Gd. m. A."


# ---------------------------------------------------------------------------
# format_pastor
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("contributor, expected", [
    ("Pastor Mueller",                    "P. Mueller"),
    ("Pastorin Schmidt",                  "Pn. Schmidt"),
    ("Diakon Weber",                      "Diakon Weber"),
    ("Diakonin Meier",                    "Diakonin Meier"),
    ("Pastor Mueller & Pastorin Schmidt", "P. Mueller, Pn. Schmidt"),
    ("Prädikantin Schulz",               "Prädikantin Schulz"),
    ("R. Bauer",                          "R. Bauer"),
    ("",                                  ""),
    ("Pastor Soost & Team",               "P. Soost & Team"),
    ("Pastorin Braun und Pastor Klein",   "Pn. Braun, P. Klein"),
])
def test_format_pastor(contributor, expected):
    assert format_pastor(contributor) == expected


# ---------------------------------------------------------------------------
# extract_boyens_location (for_export=True)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("location_name, expected", [
    # Multi-church city Heide: space-separated, no separator
    ("Heide St.-Jürgen-Kirche",     "Heide, St.-Jürgen"),
    ("Heide Erlöserkirche",          "Heide, Erlöserkirche"),
    ("Heide Auferstehungskirche",    "Heide, Auferstehungskirche"),
    # Heide-Süderholm: hyphenated compound, must NOT be split
    ("Heide-Süderholm",             "Heide-Süderholm"),
    # Single-church towns: strip trailing " Kirche"
    ("Hennstedt Kirche",            "Hennstedt"),
    ("Hemme Kirche",                "Hemme"),
    ("Lunden Kirche",               "Lunden"),
    ("Weddingstedt Kirche",         "Weddingstedt"),
    ("Schlichting Kirche",          "Schlichting"),
    ("St. Annen Kirche",            "St. Annen"),
    # Büsum with dash separator
    ("Büsum - St. Clemens-Kirche",  "Büsum"),
    ("Büsum - Perlebucht",          "Büsum, Perlebucht"),
    # Existing pipe/comma cases still pass
    ("Heide | St.-Jürgen-Kirche",  "Heide, St.-Jürgen"),
    ("Büsum | St. Clemens-Kirche", "Büsum"),
    ("Büsum | Perlebucht",         "Büsum, Perlebucht"),
    ("Hennstedt",                  "Hennstedt"),
])
def test_extract_boyens_location(location_name, expected):
    assert extract_boyens_location(location_name, for_export=True) == expected


# ---------------------------------------------------------------------------
# extract_boyens_location (for_export=False) — display mode
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("location_name, expected", [
    # St. Clemens ist NICHT Urlauberseelsorge — bleibt Büsum
    ("Büsum - St. Clemens-Kirche",  "Büsum"),
    # Urlauberseelsorge → Urlauberseelsorge in display mode
    ("Urlauberseelsorge",           "Urlauberseelsorge"),
    ("Urlauberseelsorge Büsum",     "Urlauberseelsorge"),
])
def test_extract_boyens_location_display(location_name, expected):
    assert extract_boyens_location(location_name, for_export=False) == expected


# ---------------------------------------------------------------------------
# format_service_type — Sonderformat (Kolon-Titel)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("titel, expected", [
    # Kolon-Titel: Abendmahl vor dem Kolon erkannt
    ("Gottesdienst mit Tisch-Abendmahl: Brot des Lebens", "Gd. m. A."),
    # "zum Karfreitag mit Abendmahl" — Abendmahl im Titel ohne Kolon
    ("Gottesdienst zum Karfreitag mit Abendmahl",          "Gd. m. A."),
    # Normaler Sondertitel ohne Sondertyp
    ("Gottesdienst zum Ostersonntag",                      "Gd."),
])
def test_format_service_type_sonderformat(titel, expected):
    assert format_service_type(titel) == expected
