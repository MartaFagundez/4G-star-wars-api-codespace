"""empty message

Revision ID: 5a47ef3de79d
Revises: a586ea6290db
Create Date: 2023-12-18 20:58:16.219135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a47ef3de79d'
down_revision = 'a586ea6290db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('FavoriteCharacters', schema=None) as batch_op:
        batch_op.drop_constraint('FavoriteCharacters_character_id_key', type_='unique')

    with op.batch_alter_table('FavoritePlanets', schema=None) as batch_op:
        batch_op.drop_constraint('FavoritePlanets_planet_id_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('FavoritePlanets', schema=None) as batch_op:
        batch_op.create_unique_constraint('FavoritePlanets_planet_id_key', ['planet_id'])

    with op.batch_alter_table('FavoriteCharacters', schema=None) as batch_op:
        batch_op.create_unique_constraint('FavoriteCharacters_character_id_key', ['character_id'])

    # ### end Alembic commands ###
