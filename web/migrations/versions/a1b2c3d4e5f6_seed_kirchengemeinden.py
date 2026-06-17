"""seed einzelne Kirchengemeinden (10 weitere Organisationen)

Revision ID: a1b2c3d4e5f6
Revises: f8614177200d
Create Date: 2026-06-17 15:30:00.000000

Ergaenzt die 10 einzelnen Kirchengemeinde-Organisationen, deren API-Tokens
aus der ChurchDesk-Mail stammen. Org-IDs wurden ueber den Gesamtkalender
(kirche-dithmarschen.de) und die ChurchDesk-API verifiziert (HTTP 200).
Idempotent: bestehende Eintraege (gleiche id) werden nicht doppelt angelegt.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f8614177200d'
branch_labels = None
depends_on = None


# (id, name, token, description)
SEED = [
    (2619, 'Kirchengemeinde Meldorf',           'db89f6f7851ba1d935e0022a5f0a631936b6256fa33336cf6b2e2250a643f9fd', ''),
    (2718, 'Kirchengemeinde Wöhrden',           'a85a934d8911d384e5924f75a79f1a75abac327dc9f639acf4c29a2c1bb4f34c', ''),
    (2722, 'Kirchengemeinde Lohe-Rickelshof',   '334d99d8e81d6164803d3a5c6b0a30d5925e368cc7d0a9b55d7dd6381f7dbe32', ''),
    (2723, 'Kirchengemeinde Pahlen / Delve',    '9d81fceba6810dfdc7713da617fc92c7139dea1772e6af2b8ca14f85a10ad805', ''),
    (2753, 'Kirchengemeinde Albersdorf',        '1f4807afcadb5126dbb0794a625a31a7d6db48ee69d62fb1c99ac6bb245c16e8', ''),
    (2936, 'Kirchengemeinde St. Michaelisdonn', '4d42adf9503884027d03b64923aded11025c6e7ff8a81be6f88349ab1822ac36', ''),
    (2940, 'Kirchengemeinde Süderhastedt',      'e82cc94836ea91ea9848247e4141361babb5931bf369bc4e4ca145eacaad3f9e', ''),
    (2724, 'Kirchengemeinde Tellingstedt',      '42a459ace38a5b29627a1d6cac477fc3221a762acb2f37aab7c9c18054925a20', ''),
    (2715, 'Kirchengemeinde Windbergen-Gudendorf', '7c6b6bdc16715cad87f35f7952e2b6b3eb7a7488b7ca9f62430b3d557e47ac18', ''),
    (2720, 'Kirchspiel Süd',                    '10aac750e22081eff40f409fdb30ffa0ae1bfa8ea425586649f598c1aaf14da2',
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
    to_insert = [
        {'id': oid, 'name': name, 'token': tok, 'description': desc, 'is_active': True}
        for (oid, name, tok, desc) in SEED if oid not in existing
    ]
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
