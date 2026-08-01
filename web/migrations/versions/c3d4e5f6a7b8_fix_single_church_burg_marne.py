"""fix single_church Burg/Marne — aus multi_church-Regeln entfernen

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-17 20:00:00.000000

Burg und Marne sind Single-Church-Orte (je eine Kirche) und sollen nicht
als Multi-Kirchen-Orte behandelt werden. Damit gibt extract_boyens_location
fuer Burg/Marne "Ort, Kirche" aus statt eines konkreten Kirchennamens.

Daten-Korrektur ist idempotent: DELETE auf nicht-existente Rows ist
wirkungslos. Kein Schema-Change.
"""
from alembic import op


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    # Idempotentes DELETE — laeuft auf bereits-geloeschten Rows wirkungslos.
    op.execute(
        "DELETE FROM location_rules WHERE kind = 'multi_church' AND key IN ('burg', 'marne')"
    )


def downgrade():
    # Seed-Zustand wiederherstellen. INSERT OR IGNORE fuer SQLite-Idempotenz
    # (verhindert UniqueConstraint-Fehler falls Zeilen bereits existieren).
    op.execute(
        "INSERT OR IGNORE INTO location_rules (kind, key, value, is_active)"
        " VALUES ('multi_church', 'burg', '', 1), ('multi_church', 'marne', '', 1)"
    )
