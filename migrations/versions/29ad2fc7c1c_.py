"""empty message

Revision ID: 29ad2fc7c1c
Revises: 36f8d7273ab
Create Date: 2015-08-05 19:43:36.541090

"""

# revision identifiers, used by Alembic.
revision = '29ad2fc7c1c'
down_revision = '36f8d7273ab'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_images', sa.Column('full_path', sa.String(length=256), nullable=True))
    op.add_column('product_images', sa.Column('thumb_path', sa.String(length=256), nullable=True))
    #op.drop_column('product_images', 'path')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('product_images', sa.Column('path', sa.VARCHAR(length=128), nullable=True))
    op.drop_column('product_images', 'thumb_path')
    op.drop_column('product_images', 'full_path')
    ### end Alembic commands ###