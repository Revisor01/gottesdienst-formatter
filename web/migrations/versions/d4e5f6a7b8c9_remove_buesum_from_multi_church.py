"""Büsum aus multi_church-Regeln entfernen — kein Multi-Kirchen-Ort

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-17 21:10:00.000000

"""
from alembic import op


revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    # Idempotentes DELETE — laeuft auf bereits-geloeschten Rows wirkungslos.
    op.execute(
        "DELETE FROM location_rules WHERE kind = 'multi_church' AND key = 'büsum'"
    )


def downgrade():
    # Seed-Zustand wiederherstellen. INSERT OR IGNORE fuer SQLite-Idempotenz.
    op.execute(
        "INSERT OR IGNORE INTO location_rules (kind, key, value, is_active)"
        " VALUES ('multi_church', 'büsum', '', 1)"
    )
