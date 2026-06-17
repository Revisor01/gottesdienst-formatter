"""add location_rules table + seed aktuelle Werte

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-17 16:30:00.000000

Macht die Location-Listen (Orts-Mappings, Multi-Kirchen-Orte, Nicht-Kirchen-
Stichwoerter) ueber die Admin-Oberflaeche pflegbar. Seedet die bisher
hartkodierten Werte aus churchdesk_api.py.
"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


# (kind, key, value) — gespiegelt aus den bisherigen Code-Konstanten
_MAPPINGS = {
    'st. annen-kirche': 'St. Annen',
    'st. marien-kirche': 'Eddelak',
    'marien-kirche': 'Eddelak',
    'st. laurentius-kirche': 'Lunden',
    'st. rochus-kirche': 'Schlichting',
    'st. andreas-kirche': 'Weddingstedt',
    'st. secundus-kirche': 'Hennstedt',
    'st. bartholomäus': 'Wesselburen',
    'kreuzkirche wesseln': 'Wesseln',
    'kirche wesseln': 'Wesseln',
    'st. martins-kirche': 'Tellingstedt',
    'st. martinskirche': 'Tellingstedt',
    'st. martins-kirche tellingstedt': 'Tellingstedt',
    'st. martinskirche tellingstedt': 'Tellingstedt',
    'tellingstedt st. martinskirche': 'Tellingstedt',
    'tellingstedt st. marinskirche': 'Tellingstedt',
    'st. remigius-kirche': 'Albersdorf',
    'st. remigius kirche': 'Albersdorf',
    'st. remigius-kirche albersdorf': 'Albersdorf',
    'st. remigius kirche albersdorf': 'Albersdorf',
}

_MULTI = ['heide', 'brunsbüttel', 'büsum', 'burg', 'marne']

_NON_CHURCH = [
    'badestelle', 'bootshafen', 'fähranleger', 'faehranleger', 'schwimmbad',
    'sportplatz', 'reitplatz', 'grundschule', 'schule', 'schulhof', 'mühle',
    'muehle', 'hof ', 'schutzhütte', 'schutzhuette', 'forst', 'wald', 'halle',
    'gemeindehaus', 'gemeindesaal', 'saal', 'dörpshus', 'doerpshus', 'haus ',
    'gänsemarkt', 'gaensemarkt', 'markt', 'steinzeitpark', 'park', 'papenbusch',
    'familie ', 'altenhilfezentrum', 'gemeindezentrum', 'pastorat', 'küche',
    'kueche', 'blockhütte', 'blockhuette', 'feuerwehr', 'mühlenteich', 'ankerplatz',
]


def upgrade():
    table = op.create_table(
        'location_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=32), nullable=False),
        sa.Column('key', sa.String(length=256), nullable=False),
        sa.Column('value', sa.String(length=256), nullable=False, server_default=''),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kind', 'key', name='uq_locationrule_kind_key'),
    )

    rows = []
    for key, value in _MAPPINGS.items():
        rows.append({'kind': 'mapping', 'key': key, 'value': value, 'is_active': True})
    for key in _MULTI:
        rows.append({'kind': 'multi_church', 'key': key, 'value': '', 'is_active': True})
    for key in _NON_CHURCH:
        rows.append({'kind': 'non_church', 'key': key, 'value': '', 'is_active': True})
    op.bulk_insert(table, rows)


def downgrade():
    op.drop_table('location_rules')
