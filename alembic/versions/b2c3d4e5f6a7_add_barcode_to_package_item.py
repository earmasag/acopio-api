"""add_barcode_and_item_name_to_package_item

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-01

Agrega dos columnas opcionales a package_item:
  - barcode:   El código de barras escaneado (EAN-13, UPC-A, etc.)
  - item_name: El nombre del producto resuelto por la API de códigos de barras.
Ambas son nullable porque los ítems agregados manualmente no tienen estas fuentes.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('package_item', sa.Column('barcode', sa.String(50), nullable=True))
    op.add_column('package_item', sa.Column('item_name', sa.String(255), nullable=True))
    op.create_index('ix_package_item_barcode', 'package_item', ['barcode'])


def downgrade() -> None:
    op.drop_index('ix_package_item_barcode', table_name='package_item')
    op.drop_column('package_item', 'item_name')
    op.drop_column('package_item', 'barcode')
