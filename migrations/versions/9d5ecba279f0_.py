"""empty message

Revision ID: 9d5ecba279f0
Revises: 8f7e7b058160
Create Date: 2021-09-25 21:16:16.517221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d5ecba279f0'
down_revision = '8f7e7b058160'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'user', 'lxs400', ['lxs400_vc'], ['verification_code'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    # ### end Alembic commands ###
