#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest conftest: sys.path-Fix und globale Fixtures.
"""
import os
import sys

import pytest

# Fuege web/ zum Python-Pfad hinzu (Backup fuer pyproject.toml pythonpath)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import formatting


@pytest.fixture(autouse=True)
def setup_pastor_cache():
    """Setzt den Pastor-Cache fuer alle Tests die format_pastor nutzen."""
    formatting._pastor_cache = [
        {'first_name': 'Simon', 'last_name': 'Luthe', 'title': 'P.'},
        {'first_name': 'Ulrike', 'last_name': 'Verwold', 'title': 'Pn.'},
        {'first_name': 'Christian', 'last_name': 'Verwold', 'title': 'P.'},
        {'first_name': None, 'last_name': 'Mueller', 'title': 'P.'},
        {'first_name': None, 'last_name': 'Schmidt', 'title': 'Pn.'},
        {'first_name': None, 'last_name': 'Weber', 'title': 'Diakon'},
        {'first_name': None, 'last_name': 'Meier', 'title': 'Diakonin'},
        {'first_name': None, 'last_name': 'Schulz', 'title': 'Prä.'},
        {'first_name': None, 'last_name': 'Bauer', 'title': 'R.'},
        {'first_name': None, 'last_name': 'Soost', 'title': 'P.'},
        {'first_name': None, 'last_name': 'Braun', 'title': 'Pn.'},
        {'first_name': None, 'last_name': 'Klein', 'title': 'P.'},
        {'first_name': 'Ulf', 'last_name': 'Fiebrandt', 'title': 'Diakon'},
        {'first_name': 'Susanne', 'last_name': 'Jordan', 'title': 'Diakonin'},
        {'first_name': 'Frauke', 'last_name': 'Hjort', 'title': 'Prä.'},
        {'first_name': 'Astrid', 'last_name': 'Buchin', 'title': 'Pn.'},
        {'first_name': 'Claudia', 'last_name': 'Ruge-Tolksdorf', 'title': 'Pn.'},
        {'first_name': None, 'last_name': 'Stein', 'title': 'P. Dr.'},
        {'first_name': None, 'last_name': 'Petersen', 'title': 'Popkantorin'},
        {'first_name': None, 'last_name': 'Zigler', 'title': 'Jugendreferentin'},
    ]
    yield
    formatting._pastor_cache = []
