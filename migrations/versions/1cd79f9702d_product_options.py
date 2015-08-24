"""product options

Revision ID: 1cd79f9702d
Revises: 3ca84356c8c
Create Date: 2015-08-22 09:28:32.022089

"""

# revision identifiers, used by Alembic.
revision = '1cd79f9702d'
down_revision = '3ca84356c8c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.drop_column('product_images', 'path')
    op.add_column('product_options', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('product_options', sa.Column('quantity', sa.Integer(), nullable=True))
    op.create_index('ix_product_options_price', 'product_options', ['price'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_product_options_price', 'product_options')
    op.drop_column('product_options', 'quantity')
    op.drop_column('product_options', 'price')
    #op.add_column('product_images', sa.Column('path', sa.VARCHAR(length=128), nullable=True))
    ### end Alembic commands ###
