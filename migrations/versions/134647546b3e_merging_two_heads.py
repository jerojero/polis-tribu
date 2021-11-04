"""merging two heads

Revision ID: 134647546b3e
Revises: d92fffef78e3, ba0c1b0a646f
Create Date: 2021-10-17 18:10:17.389945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '134647546b3e'
down_revision = ('d92fffef78e3', 'ba0c1b0a646f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
