"""create_users_table

Revision ID: 251d6e5e9c01
Revises: 
Create Date: 2026-04-07 15:30:38.136835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '251d6e5e9c01'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')