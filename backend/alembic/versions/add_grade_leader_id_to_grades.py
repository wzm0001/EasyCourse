"""add grade_leader_id to grades

Revision ID: add_grade_leader_id_to_grades
Revises: rename_teacher_id_to_head_teacher_id
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_grade_leader_id_to_grades'
down_revision = 'rename_teacher_id_to_head_teacher_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('grades', schema=None) as batch_op:
        batch_op.add_column(sa.Column('grade_leader_id', sa.String(36), nullable=True))
        batch_op.create_foreign_key('fk_grades_grade_leader_id', 'teachers', ['grade_leader_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('grades', schema=None) as batch_op:
        batch_op.drop_constraint('fk_grades_grade_leader_id', type_='foreignkey')
        batch_op.drop_column('grade_leader_id')
