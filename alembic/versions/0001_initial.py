"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-29 13:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # camp_token
    op.create_table('camp_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=255), nullable=False),
    sa.Column('camp_name', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_camp_token_id'), 'camp_token', ['id'], unique=False)
    op.create_index(op.f('ix_camp_token_token_hash'), 'camp_token', ['token_hash'], unique=True)

    # category
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=False)

    # sync_log
    op.create_table('sync_log',
    sa.Column('sync_id', sa.String(length=36), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('result', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('sync_id')
    )

    # truck
    op.create_table('truck',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('license_plate', sa.String(length=15), nullable=False),
    sa.Column('driver_name', sa.String(length=100), nullable=False),
    sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('license_plate')
    )
    op.create_index(op.f('ix_truck_id'), 'truck', ['id'], unique=False)

    # trip
    op.create_table('trip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('truck_id', sa.Integer(), nullable=False),
    sa.Column('origin_camp', sa.String(length=50), nullable=False),
    sa.Column('destination_camp', sa.String(length=50), nullable=False),
    sa.Column('dispatched_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), server_default='CREATING', nullable=False),
    sa.ForeignKeyConstraint(['truck_id'], ['truck.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trip_id'), 'trip', ['id'], unique=False)

    # package
    op.create_table('package',
    sa.Column('id_uuid', sa.String(length=36), nullable=False),
    sa.Column('trip_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=25), nullable=False),
    sa.Column('packer_name', sa.String(length=100), nullable=True),
    sa.Column('receiver_name', sa.String(length=100), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['trip_id'], ['trip.id'], ),
    sa.PrimaryKeyConstraint('id_uuid')
    )

    # package_item
    op.create_table('package_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package_uuid', sa.String(length=36), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.CheckConstraint('quantity > 0', name='chk_quantity'),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['package_uuid'], ['package.id_uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_package_item_id'), 'package_item', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_package_item_id'), table_name='package_item')
    op.drop_table('package_item')
    op.drop_table('package')
    op.drop_index(op.f('ix_trip_id'), table_name='trip')
    op.drop_table('trip')
    op.drop_index(op.f('ix_truck_id'), table_name='truck')
    op.drop_table('truck')
    op.drop_table('sync_log')
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.drop_table('category')
    op.drop_index(op.f('ix_camp_token_token_hash'), table_name='camp_token')
    op.drop_index(op.f('ix_camp_token_id'), table_name='camp_token')
    op.drop_table('camp_token')
