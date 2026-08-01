"""Büsum aus multi_church-Regeln entfernen — kein Multi-Kirchen-Ort

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-17 21:10:00.000000

Büsum hat nur eine Kirche (St. Clemens) und ist damit KEIN Multi-Kirchen-Ort.
Die Seed-Migration b2c3d4e5f6a7 hatte 'büsum' faelschlich als multi_church
eingetragen. Diese Regel wird entfernt, damit load_location_rules Büsum nicht
wieder in MULTI_CHURCH_CITIES laedt — Büsum laeuft dann durch die normale
Einzelkirchen-Logik ("Büsum, Kirche" / "Büsum, Perlebucht").

Daten-Korrektur ist idempotent: DELETE auf nicht-existente Rows ist wirkungslos.
Kein Schema-Change.
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
