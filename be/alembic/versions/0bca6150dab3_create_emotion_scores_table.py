"""create_emotion_scores_table

Revision ID: 0bca6150dab3
Revises: seed_cv_scenarios
Create Date: 2025-11-15 21:47:58.022461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bca6150dab3'
down_revision: Union[str, Sequence[str], None] = 'seed_cv_scenarios'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
