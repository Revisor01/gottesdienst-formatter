#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest conftest: sys.path-Fix damit `from formatting import ...` funktioniert.
"""
import os
import sys

# Fuege web/ zum Python-Pfad hinzu (Backup fuer pyproject.toml pythonpath)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
