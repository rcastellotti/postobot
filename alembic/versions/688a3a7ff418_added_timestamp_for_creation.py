"""added timestamp for creation

Revision ID: 688a3a7ff418
Revises: 
Create Date: 2021-09-24 09:36:34.641395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688a3a7ff418'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Lectures', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Lectures', 'created_at')
    # ### end Alembic commands ###
