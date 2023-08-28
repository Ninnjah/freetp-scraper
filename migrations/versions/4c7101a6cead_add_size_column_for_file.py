"""Add size column for file

Revision ID: 4c7101a6cead
Revises: 1c9e785fd521
Create Date: 2023-08-28 19:23:53.418046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c7101a6cead'
down_revision: Union[str, None] = '1c9e785fd521'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('size', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'size')
    # ### end Alembic commands ###