"""Self referential relationship on Question

Revision ID: 554aa275df4c
Revises: dc77ee2c300b
Create Date: 2021-10-12 18:00:20.209277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '554aa275df4c'
down_revision = 'dc77ee2c300b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('head', sa.Boolean(), nullable=True))
    op.add_column('question', sa.Column('next_question', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'next_question')
    op.drop_column('question', 'head')
    # ### end Alembic commands ###
