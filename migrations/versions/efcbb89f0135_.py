"""empty message

Revision ID: efcbb89f0135
Revises: c10f02b32b52
Create Date: 2020-11-14 22:33:35.061255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efcbb89f0135'
down_revision = 'c10f02b32b52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artists', sa.Column('website', sa.String(length=500), nullable=True))
    op.add_column('shows', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.add_column('shows', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'shows', 'artists', ['artist_id'], ['id'])
    op.create_foreign_key(None, 'shows', 'venues', ['venue_id'], ['id'], ondelete='CASCADE')
    op.add_column('venues', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    op.drop_column('venues', 'seeking_talent')
    op.drop_column('venues', 'seeking_description')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_column('shows', 'venue_id')
    op.drop_column('shows', 'artist_id')
    op.drop_column('artists', 'website')
    op.drop_column('artists', 'seeking_venue')
    op.drop_column('artists', 'seeking_description')
    # ### end Alembic commands ###