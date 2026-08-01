"""add_service_type_mappings_table

Revision ID: f1a2b3c4d5e6
Revises: e4f63c8b0c96
Create Date: 2026-03-22 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e4f63c8b0c96'
branch_labels = None
depends_on = None


def upgrade():
    mappings_table = op.create_table('service_type_mappings',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('keyword', sa.String(length=256), nullable=False),
    sa.Column('output_label', sa.String(length=256), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('keyword')
    )

    # Seed: Wohnzimmerkirche
    op.bulk_insert(mappings_table, [
        {
            'keyword': 'wohnzimmerkirche',
            'output_label': 'Wz-Gd.',
            'priority': 100,
            'is_active': True,
        },
    ])


def downgrade():
    op.drop_table('service_type_mappings')
