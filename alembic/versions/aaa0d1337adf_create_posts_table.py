"""create_posts_table

Revision ID: aaa0d1337adf
Revises: 251d6e5e9c01
Create Date: 2026-04-07 15:31:38.402767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaa0d1337adf'
down_revision: Union[str, Sequence[str], None] = '251d6e5e9c01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('published', sa.Boolean(), server_default='True'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], 
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('posts')