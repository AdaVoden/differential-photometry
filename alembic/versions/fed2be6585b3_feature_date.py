"""feature_date

Revision ID: fed2be6585b3
Revises: a4fd7959c202
Create Date: 2022-05-17 12:26:20.940794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fed2be6585b3'
down_revision = 'a4fd7959c202'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('features', sa.Column('date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('features', 'date')
    # ### end Alembic commands ###
