"""rename teacher_id to head_teacher_id in classes

Revision ID: rename_teacher_id_to_head_teacher_id
Revises: remove_is_fixed_from_schedule_cells
Create Date: 2026-05-08

"""
from alembic import op
import sqlalchemy as sa


revision = 'rename_teacher_id_to_head_teacher_id'
down_revision = 'remove_is_fixed_from_schedule_cells'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.alter_column('teacher_id', new_column_name='head_teacher_id')


def downgrade() -> None:
    with op.batch_alter_table('classes', schema=None) as batch_op:
        batch_op.alter_column('head_teacher_id', new_column_name='teacher_id')
