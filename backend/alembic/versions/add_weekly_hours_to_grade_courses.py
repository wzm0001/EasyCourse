"""add weekly_hours to grade_courses

Revision ID: add_weekly_hours_to_grade_courses
Revises: 
Create Date: 2026-05-07

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_weekly_hours_to_grade_courses'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('grade_courses', sa.Column('weekly_hours', sa.Integer(), nullable=True, server_default='1'))
    op.execute("UPDATE grade_courses SET weekly_hours = 1 WHERE weekly_hours IS NULL")
    op.alter_column('grade_courses', 'weekly_hours', nullable=False)


def downgrade() -> None:
    op.drop_column('grade_courses', 'weekly_hours')
