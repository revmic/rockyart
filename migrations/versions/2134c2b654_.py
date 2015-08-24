"""empty message

Revision ID: 2134c2b654
Revises: 1902ec4cf88
Create Date: 2015-08-21 00:05:11.894823

"""

# revision identifiers, used by Alembic.
revision = '2134c2b654'
down_revision = '1902ec4cf88'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    #op.drop_column('product_images', 'path')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('product_images', sa.Column('path', sa.VARCHAR(length=128), nullable=True))
    op.drop_table('product_options')
    ### end Alembic commands ###