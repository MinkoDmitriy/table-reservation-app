"""add restaurant_managers table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-14 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('restaurant_managers',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('food_place_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['food_place_id'], ['food_places.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'food_place_id'),
    )


def downgrade() -> None:
    op.drop_table('restaurant_managers')
