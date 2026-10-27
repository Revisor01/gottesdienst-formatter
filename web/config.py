#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Organisationen kommen allein aus der Tabelle organizations, nicht aus der Umgebung."""

# Modul-level dict — wird bei App-Start gefuellt und nach Admin-Aenderungen aktualisiert.
ORGANIZATIONS: dict = {}


def load_organizations() -> dict:
    """Aktive Organisationen als {org_id: {name, token, description}}; braucht einen App-Kontext."""
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
    """Nach Admin-Änderungen aufrufen, damit churchdesk_api.py den aktuellen Stand sieht."""
    global ORGANIZATIONS
    ORGANIZATIONS.clear()
    ORGANIZATIONS.update(load_organizations())
