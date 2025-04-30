"""Add OTP model and phone number to User

Revision ID: custom_migration_1
Revises: 
Create Date: 2025-04-13 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'custom_migration_1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create OTP table
    op.create_table('otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otps_id'), 'otps', ['id'], unique=False)
    
    # Add phone_number to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
        op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    except Exception:
        # Column may already exist, continue
        pass


def downgrade() -> None:
    # Drop OTP table
    op.drop_index(op.f('ix_otps_id'), table_name='otps')
    op.drop_table('otps')
    
    # Remove phone_number from users table
    try:
        op.drop_index(op.f('ix_users_phone_number'), table_name='users')
        op.drop_column('users', 'phone_number')
    except Exception:
        pass
