"""add_clothing_detail_and_seed_categories

Revision ID: a1b2c3d4e5f6
Revises: 898ba293865e
Create Date: 2026-07-01

Crea la tabla clothing_item_detail para prendas de ropa con talla,
actualiza category para usar IDs de texto (slug) para coincidir
exactamente con el frontend, y siembra las categorías y tipos de prenda.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '898ba293865e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Agregar columna slug a category (coincide con CategoryId del front) ──
    op.add_column('category', sa.Column('slug', sa.String(50), nullable=True, unique=True))

    # ── 2. Crear tabla garment_type (tipos de prenda) ──
    op.create_table(
        'garment_type',
        sa.Column('id', sa.String(50), primary_key=True),   # e.g. "camisa", "calzado"
        sa.Column('label', sa.String(100), nullable=False),
    )

    # ── 3. Crear tabla clothing_item_detail ──
    op.create_table(
        'clothing_item_detail',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('package_item_id', sa.Integer(),
                  sa.ForeignKey('package_item.id', ondelete='CASCADE'),
                  nullable=False, unique=True),
        sa.Column('garment_type_id', sa.String(50),
                  sa.ForeignKey('garment_type.id'),
                  nullable=False),
        # Talla: texto libre para soportar XS/S/M/L/XL/XXL/2XL/Única y números de calzado (35-48)
        sa.Column('size', sa.String(10), nullable=False),
    )
    op.create_index('ix_clothing_item_detail_id', 'clothing_item_detail', ['id'])
    op.create_index('ix_clothing_item_detail_package_item_id',
                    'clothing_item_detail', ['package_item_id'], unique=True)

    # ── 4. Sembrar categorías (IDs numéricos + slug que coincide con el front) ──
    category_table = table('category',
        column('id', sa.Integer),
        column('name', sa.String),
        column('slug', sa.String),
        column('description', sa.String),
    )
    op.bulk_insert(category_table, [
        {'id': 1, 'name': 'Medicamentos',    'slug': 'medicamentos',   'description': 'Pastillas, jarabes y similares'},
        {'id': 2, 'name': 'Insumos médicos', 'slug': 'insumos_medicos','description': 'Vendas, jeringas, artículos de higiene'},
        {'id': 3, 'name': 'Comida',          'slug': 'comida',         'description': 'Alimentos no perecederos'},
        {'id': 4, 'name': 'Bebida',          'slug': 'bebida',         'description': 'Agua, jugos y bebidas'},
        {'id': 5, 'name': 'Ropa',            'slug': 'ropa',           'description': 'Prendas de vestir y calzado'},
        {'id': 6, 'name': 'Juguetes',        'slug': 'juguetes',       'description': 'Juguetes y libros infantiles'},
    ])

    # ── 5. Sembrar tipos de prenda (IDs coinciden exactamente con GarmentTypeId del front) ──
    garment_type_table = table('garment_type',
        column('id', sa.String),
        column('label', sa.String),
    )
    op.bulk_insert(garment_type_table, [
        {'id': 'camisa',        'label': 'Camisa'},
        {'id': 'pantalon',      'label': 'Pantalón'},
        {'id': 'short',         'label': 'Short'},
        {'id': 'falda',         'label': 'Falda'},
        {'id': 'vestido',       'label': 'Vestido'},
        {'id': 'chaqueta',      'label': 'Chaqueta / abrigo'},
        {'id': 'calzado',       'label': 'Calzado'},
        {'id': 'ropa_interior', 'label': 'Ropa interior'},
        {'id': 'otro',          'label': 'Otra'},
    ])


def downgrade() -> None:
    op.drop_index('ix_clothing_item_detail_package_item_id', table_name='clothing_item_detail')
    op.drop_index('ix_clothing_item_detail_id', table_name='clothing_item_detail')
    op.drop_table('clothing_item_detail')
    op.drop_table('garment_type')
    op.drop_column('category', 'slug')
