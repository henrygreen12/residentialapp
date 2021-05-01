"""output and survey

Revision ID: 6b9d5b0a5b06
Revises: 02e2656930fe
Create Date: 2021-04-07 01:15:46.414682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b9d5b0a5b06'
down_revision = '02e2656930fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey', sa.Column('cookFrequency', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('dishWasher', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('hotWaterUsage', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('houseStories', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('laundryUsage', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('microwaveFrequency', sa.String(length=200), nullable=True))
    op.add_column('survey', sa.Column('numOfPeople', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('survey', 'numOfPeople')
    op.drop_column('survey', 'microwaveFrequency')
    op.drop_column('survey', 'laundryUsage')
    op.drop_column('survey', 'houseStories')
    op.drop_column('survey', 'hotWaterUsage')
    op.drop_column('survey', 'dishWasher')
    op.drop_column('survey', 'cookFrequency')
    # ### end Alembic commands ###
