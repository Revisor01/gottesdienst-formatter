#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfiguration fuer ChurchDesk-Organisationen.
Laedt Organisationen aus der SQLite-Datenbank (Tabelle: organizations).
Single source of truth — keine Environment-Variablen fuer Org-Daten mehr.
"""

# Modul-level dict — wird bei App-Start gefuellt und nach Admin-Aenderungen aktualisiert.
ORGANIZATIONS: dict = {}


def load_organizations() -> dict:
    """Laedt alle aktiven Organisationen aus der Datenbank.

    Muss innerhalb eines Flask-App-Kontexts aufgerufen werden.

    Returns:
        {org_id: {"name": str, "token": str, "description": str}, ...}
    """
    from models import Organization
    orgs = {}
    try:
        for org in Organization.query.filter_by(is_active=True).all():
            orgs[org.id] = {
                'name': org.name,
                'token': org.token,
                'description': org.description or '',
            }
    except Exception:
        # Falls DB noch nicht initialisiert (z.B. erster Start vor Migration)
        pass
    return orgs


def reload_organizations() -> None:
    """Aktualisiert das modul-level ORGANIZATIONS-Dict aus der DB.

    Nach Admin-CRUD-Operationen aufrufen, damit aendernde Abfragen
    in churchdesk_api.py den aktuellen Stand sehen.
    """
    global ORGANIZATIONS
    ORGANIZATIONS.clear()
    ORGANIZATIONS.update(load_organizations())
