"""Add health record models

Revision ID: add_health_record_models
Depends on: 52de63f8bcbc
Create Date: 2023-05-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from enum import Enum

# revision identifiers, used by Alembic.
revision = 'add_health_record_models'
down_revision = '52de63f8bcbc'  # Adjust this to your latest migration
branch_labels = None
depends_on = None


class RecordType(str, Enum):
    GENERAL = "general"
    VACCINATION = "vaccination"
    TREATMENT = "treatment"
    WEIGHT = "weight"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


def upgrade():
    # Create health_records table
    op.create_table(
        'health_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.Enum('general', 'vaccination', 'treatment', 'weight', name='recordtype'), nullable=False),
        sa.Column('record_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('next_reminder_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], name='fk_health_records_pet_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_health_records_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_records_id'), 'health_records', ['id'], unique=False)
    op.create_index(op.f('ix_health_records_pet_id'), 'health_records', ['pet_id'], unique=False)
    op.create_index(op.f('ix_health_records_user_id'), 'health_records', ['user_id'], unique=False)

    # Create health_record_media table
    op.create_table(
        'health_record_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('health_record_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.Enum('image', 'video', 'document', name='mediatype'), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], name='fk_health_record_media_record_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_record_media_id'), 'health_record_media', ['id'], unique=False)
    op.create_index(op.f('ix_health_record_media_health_record_id'), 'health_record_media', ['health_record_id'], unique=False)


def downgrade():
    # Drop tables in the correct order
    op.drop_table('health_record_media')
    op.drop_table('health_records')
    
    # Drop the enum types if your database supports it (MySQL doesn't need this)
    # op.execute('DROP TYPE mediatype')
    # op.execute('DROP TYPE recordtype')
