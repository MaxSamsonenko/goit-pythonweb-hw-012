"""add role to users

Revision ID: 61523c94862c
Revises: bbcd0b5df4d4
Create Date: 2025-04-10 14:41:40.464739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61523c94862c'
down_revision: Union[str, None] = 'bbcd0b5df4d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
