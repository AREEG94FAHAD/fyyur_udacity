"""empty message

Revision ID: 68f653083f81
Revises: 7f7ed0abab5d
Create Date: 2020-04-13 05:01:33.872081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68f653083f81'
down_revision = '7f7ed0abab5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###