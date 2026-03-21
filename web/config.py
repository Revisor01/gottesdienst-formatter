#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfiguration fuer ChurchDesk-Organisationen.
Laedt alle Credentials aus Environment Variables — keine hardcoded Tokens.
"""
import os


def load_organizations() -> dict:
    """Laedt Organisationskonfiguration aus Env-Vars.

    Erwartet:
        CHURCHDESK_ORG_IDS=2596,6572,2719,2725,2729
        CHURCHDESK_ORG_{ID}_NAME=Kirchspiel Heide
        CHURCHDESK_ORG_{ID}_TOKEN=abc123...
        CHURCHDESK_ORG_{ID}_DESCRIPTION=Heide (St.-Juergen...)  # optional
    """
    org_ids_str = os.getenv('CHURCHDESK_ORG_IDS', '')
    if not org_ids_str:
        return {}

    orgs = {}
    for org_id_str in org_ids_str.split(','):
        org_id = int(org_id_str.strip())
        prefix = "CHURCHDESK_ORG_{}_".format(org_id)
        name = os.getenv("{}NAME".format(prefix))
        token = os.getenv("{}TOKEN".format(prefix))
        if name and token:
            orgs[org_id] = {
                'name': name,
                'token': token,
                'description': os.getenv("{}DESCRIPTION".format(prefix), '')
            }
    return orgs


ORGANIZATIONS = load_organizations()
