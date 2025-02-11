# migrations/versions/initial_migration.py

"""initial migration

Revision ID: initial
Revises: 
Create Date: 

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

def upgrade():
    # Create tables
    op.create_table(
        'arrivals_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_date', sa.Date(), nullable=False),
        # ... other columns ...
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indices
    op.create_index(
        'idx_origin_geom',
        'arrivals_tracking',
        ['origin_geom'],
        postgresql_using='gist'
    )

def downgrade():
    op.drop_table('arrivals_tracking')