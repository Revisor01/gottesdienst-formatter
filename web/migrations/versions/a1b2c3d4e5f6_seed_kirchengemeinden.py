"""seed einzelne Kirchengemeinden (10 weitere Organisationen)

Revision ID: a1b2c3d4e5f6
Revises: f8614177200d
Create Date: 2026-06-17 15:30:00.000000

Ergaenzt die 10 einzelnen Kirchengemeinde-Organisationen. Org-IDs wurden ueber
den Gesamtkalender (kirche-dithmarschen.de) und die ChurchDesk-API verifiziert
(HTTP 200). Die API-Tokens kommen aus der Umgebung (CHURCHDESK_ORG_<ID>_TOKEN),
nie aus dem Code.
Idempotent: bestehende Eintraege (gleiche id) werden nicht doppelt angelegt.
"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f8614177200d'
branch_labels = None
depends_on = None


# (id, name, description) — Tokens kommen aus CHURCHDESK_ORG_<ID>_TOKEN.
SEED = [
    (2619, 'Kirchengemeinde Meldorf',           ''),
    (2718, 'Kirchengemeinde Wöhrden',           ''),
    (2722, 'Kirchengemeinde Lohe-Rickelshof',   ''),
    (2723, 'Kirchengemeinde Pahlen / Delve',    ''),
    (2753, 'Kirchengemeinde Albersdorf',        ''),
    (2936, 'Kirchengemeinde St. Michaelisdonn', ''),
    (2940, 'Kirchengemeinde Süderhastedt',      ''),
    (2724, 'Kirchengemeinde Tellingstedt',      ''),
    (2715, 'Kirchengemeinde Windbergen-Gudendorf', ''),
    (2720, 'Kirchspiel Süd',
           'Brunsbüttel, Burg, Eddelak, Marne, St. Michaelisdonn, Vereinigte Köge'),
]

SEED_IDS = [row[0] for row in SEED]


def upgrade():
    # Idempotenter Seed: nur Eintraege anlegen, die noch nicht existieren.
    conn = op.get_bind()
    existing = {
        r[0] for r in conn.execute(
            sa.text("SELECT id FROM organizations WHERE id IN ({})".format(
                ','.join(str(i) for i in SEED_IDS)
            ))
        )
    }
    # Nur Orgs anlegen, die noch nicht existieren UND deren Token in der
    # Umgebung steht. Ohne Token wird die Org uebersprungen.
    to_insert = []
    for oid, name, desc in SEED:
        if oid in existing:
            continue
        token = os.environ.get('CHURCHDESK_ORG_{}_TOKEN'.format(oid))
        if not token:
            continue
        to_insert.append({
            'id': oid, 'name': name, 'token': token,
            'description': desc, 'is_active': True,
        })
    if to_insert:
        org_table = sa.table(
            'organizations',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('token', sa.Text),
            sa.column('description', sa.Text),
            sa.column('is_active', sa.Boolean),
        )
        op.bulk_insert(org_table, to_insert)


def downgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM organizations WHERE id IN ({})".format(
            ','.join(str(i) for i in SEED_IDS)
        ))
    )
