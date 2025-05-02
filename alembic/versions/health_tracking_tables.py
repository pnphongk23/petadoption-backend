"""add health tracking tables - DEPRECATED/UNUSED

Revision ID: health_tracking_tables_deprecated
Create Date: 2025-05-01 14:30:00

WARNING: THIS FILE IS DEPRECATED AND SHOULD NOT BE USED.
The functionality has been moved to add_health_record_models.py
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# This migration is intentionally disabled 
# The proper health record tables are created in add_health_record_models.py
revision = 'health_tracking_tables_deprecated'  # Unique ID that won't conflict
down_revision = '52de63f8bcbc'  # Attach to main migration chain to avoid multiple heads
branch_labels = None
depends_on = None


def upgrade():
    # This migration is disabled - do nothing
    pass


def downgrade():
    # This migration is disabled - do nothing
    pass
