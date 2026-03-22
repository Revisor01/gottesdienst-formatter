#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-Tests fuer alle Formatierungsfunktionen in web/formatting.py.
"""
import pytest
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


def test_format_date_none():
    assert format_date(None) == ""


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


def test_format_time_none():
    assert format_time(None) == ""


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


def test_format_service_type_none():
    assert format_service_type(None) == "Gd."
    assert format_service_type("") == "Gd."


def test_format_service_type_case_insensitive():
    # Gross-/Kleinschreibung spielt keine Rolle
    assert format_service_type("GOTTESDIENST") == "Gd."
    assert format_service_type("abendmahlsgottesdienst") == "Gd. m. A."


# ---------------------------------------------------------------------------
# format_pastor (DB-Lookup basiert)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("contributor, expected", [
    # Einfache Matches — Nachname in DB
    ("Pastor Mueller",                    "P. Mueller"),
    ("Pastorin Schmidt",                  "Pn. Schmidt"),
    ("Diakon Weber",                      "Diakon Weber"),
    ("Diakonin Meier",                    "Diakonin Meier"),
    ("Prädikantin Schulz",               "Prä. Schulz"),
    ("R. Bauer",                          "R. Bauer"),
    ("",                                  ""),
    # Mehrere Pastoren
    ("Pastor Mueller & Pastorin Schmidt", "P. Mueller, Pn. Schmidt"),
    ("Pastor Soost & Team",               "P. Soost & Team"),
    ("Pastorin Braun und Pastor Klein",   "Pn. Braun, P. Klein"),
    # Vorname wird entfernt — Nachname matcht aus DB
    ("Pastor Simon Luthe",               "P. Luthe"),
    ("Pastorin Ulrike Verwold",          "Pn. Verwold"),
    ("Diakon Ulf Fiebrandt",            "Diakon Fiebrandt"),
    ("Diakonin Susanne Jordan",         "Diakonin Jordan"),
    ("Prädikantin Frauke Hjort",        "Prä. Hjort"),
    ("Pastorin Astrid Buchin",          "Pn. Buchin"),
    # Disambiguierung — gleicher Nachname, verschiedene Titel
    ("Pastorin Ulrike Verwold, Pastor Simon Luthe", "Pn. Verwold, P. Luthe"),
    # Doppelname
    ("Pastorin Claudia Ruge-Tolksdorf", "Pn. Ruge-Tolksdorf"),
    # Dr. im Titel
    ("P. Dr. Stein",                    "P. Dr. Stein"),
    ("Pastor Dr. Stein",                "P. Dr. Stein"),
    # Durchreichen — Popkantorin, Jugendreferentin
    ("Popkantorin Petersen",            "Popkantorin Petersen"),
    ("Jugendreferentin Zigler",         "Jugendreferentin Zigler"),
    # Gruppen durchreichen (kein DB-Match)
    ("Kantorei",                        "Kantorei"),
    ("Chor Terziano",                   "Chor Terziano"),
    # Noise filtern
    ("Prädikantin in Ausbildung Frauke Hjort, dem Team der Kinderkirche, vielen Kirchenmäusen", "Prä. Hjort"),
    # Frauenhilfe durchreichen
    ("Ev. Frauenhilfe Hennstedt & Team", "Ev. Frauenhilfe Hennstedt & Team"),
    # WGT-Normalisierung
    ("Weltgebetstagsteam",               "Weltgebetstagsteam"),
    ("WGT-Team",                         "Weltgebetstagsteam"),
    ("Das Weltsgebetstagsteam Nordhastedt", "Weltgebetstagsteam"),
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
# format_service_type — Strikt Boyens: nur Typ, keine Untertitel
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("titel, expected", [
    # Doppelpunkt-Titel: nur Typ vor dem Doppelpunkt matchen, Untertitel wegwerfen
    ("Gottesdienst mit Tisch-Abendmahl: Brot des Lebens",   "Gd. m. A."),
    ("Gottesdienst mit Abendmahl: Erntedank",               "Gd. m. A."),
    ("Gottesdienst mit Taufe: Familiengottesdienst",         "Gd. m. T."),
    ("Gottesdienst mit Abendmahl und Taufe: Pfingsten",     "Abendmahlgd. m. T."),
    ("Gottesdienst: Lichterfest",                            "Gd."),
    ("Gottesdienst:",                                        "Gd."),
    # Abendmahl im Titel ohne Doppelpunkt
    ("Gottesdienst zum Karfreitag mit Abendmahl",           "Gd. m. A."),
    # Normaler Sondertitel ohne Sondertyp
    ("Gottesdienst zum Ostersonntag",                       "Gd."),
    # Anführungszeichen-Titel: auch nur Typ matchen, nicht 1:1 übernehmen
    ('\u201eUnterwegs\u201c Brotzeit: Die Wohnzimmerkirche', "Gd."),
    # Glaube und Gabel etc. — alles nur Gd.
    ("Glaube und Gabel - Die Familienkirche zum Anbeißen",  "Gd."),
])
def test_format_service_type_strikt_boyens(titel, expected):
    assert format_service_type(titel) == expected
