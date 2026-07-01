"""add_product_catalog

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-01

Tabla `product`: catálogo local que actúa como caché de consultas
a APIs externas (OpenFDA, OpenFoodFacts, UPCItemDB, etc.).
El barcode es la clave primaria (única por definición de un código de barras).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product',
        sa.Column('barcode', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(150), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('category.id'), nullable=True),
        # source_api: qué API externa identificó este producto (open_fda, upcitemdb_trial, etc.)
        sa.Column('source_api', sa.String(50), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_product_barcode', 'product', ['barcode'])
    op.create_index('ix_product_name', 'product', ['name'])


def downgrade() -> None:
    op.drop_index('ix_product_name', table_name='product')
    op.drop_index('ix_product_barcode', table_name='product')
    op.drop_table('product')
