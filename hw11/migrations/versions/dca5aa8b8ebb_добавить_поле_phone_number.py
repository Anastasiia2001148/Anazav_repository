"""Добавить поле phone_number

Revision ID: dca5aa8b8ebb
Revises: c7de8ec1681f
Create Date: 2024-10-09 23:45:27.874014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dca5aa8b8ebb'
down_revision: Union[str, None] = 'c7de8ec1681f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contapp', sa.Column('phone_number', sa.String(), nullable=True))
    op.alter_column('contapp', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('contapp', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('contapp', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('contapp', 'birthday',
               existing_type=sa.DATE(),
               nullable=True)
    op.create_index(op.f('ix_contapp_id'), 'contapp', ['id'], unique=False)
    op.drop_column('contapp', 'phone')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contapp', sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_contapp_id'), table_name='contapp')
    op.alter_column('contapp', 'birthday',
               existing_type=sa.DATE(),
               nullable=False)
    op.alter_column('contapp', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('contapp', 'last_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('contapp', 'first_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('contapp', 'phone_number')
    # ### end Alembic commands ###
