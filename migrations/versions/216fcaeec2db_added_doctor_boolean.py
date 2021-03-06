"""Added doctor boolean

Revision ID: 216fcaeec2db
Revises: 4852244d3e7e
Create Date: 2021-09-25 23:15:55.801107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '216fcaeec2db'
down_revision = '4852244d3e7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('doctor', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'doctor')
    # ### end Alembic commands ###
