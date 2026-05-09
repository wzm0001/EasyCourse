"""remove is_fixed from schedule_cells

Revision ID: remove_is_fixed_from_schedule_cells
Revises: add_weekly_hours_to_grade_courses
Create Date: 2026-05-08

"""
from alembic import op
import sqlalchemy as sa


revision = 'remove_is_fixed_from_schedule_cells'
down_revision = 'add_weekly_hours_to_grade_courses'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('schedule_cells', 'is_fixed')


def downgrade() -> None:
    op.add_column('schedule_cells', sa.Column('is_fixed', sa.Boolean(), nullable=True, server_default='0'))
