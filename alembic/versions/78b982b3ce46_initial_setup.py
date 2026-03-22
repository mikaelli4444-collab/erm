"""initial_setup

Revision ID: 78b982b3ce46
Revises: 
Create Date: 2026-03-07 21:31:44.128425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78b982b3ce46'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. CREACIÓN DE TABLAS (Sin Foreign Keys) ---

    # Tabla: companies
    op.create_table('companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('legal_name', sa.String(), nullable=False),
        sa.Column('tax_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('plan', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_email'), 'companies', ['email'], unique=True)
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_legal_name'), 'companies', ['legal_name'], unique=False)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)
    op.create_index(op.f('ix_companies_tax_id'), 'companies', ['tax_id'], unique=True)

    # Tabla: contacts
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_name'), 'contacts', ['name'], unique=False)
    op.create_index(op.f('ix_contacts_phone'), 'contacts', ['phone'], unique=True)

    # Tabla: production
    op.create_table('production',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_name', sa.String(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_client_name'), 'production', ['client_name'], unique=False)
    op.create_index(op.f('ix_production_id'), 'production', ['id'], unique=False)

    # Tabla: users
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('fullname', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_verified', sa.Integer(), nullable=False),
        sa.Column('verification_code', sa.String(), nullable=True),
        sa.Column('verification_code_expires_at', sa.DateTime(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Tabla: inventory
    op.create_table('inventory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_id'), 'inventory', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_item_name'), 'inventory', ['item_name'], unique=False)

    # --- 2. CREACIÓN DE FOREIGN KEYS (Al final, cuando todas las tablas existen) ---

    # Relación Company -> User (Owner)
    op.create_foreign_key('fk_company_owner', 'companies', 'users', ['owner_id'], ['id'])

    # Relación User -> Company
    op.create_foreign_key('fk_user_company', 'users', 'companies', ['company_id'], ['id'])

    # Relaciones Inventory -> Company y Inventory -> User
    op.create_foreign_key('fk_inventory_company', 'inventory', 'companies', ['company_id'], ['id'])
    op.create_foreign_key('fk_inventory_owner', 'inventory', 'users', ['owner_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_inventory_item_name'), table_name='inventory')
    op.drop_index(op.f('ix_inventory_id'), table_name='inventory')
    op.drop_table('inventory')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_production_id'), table_name='production')
    op.drop_index(op.f('ix_production_client_name'), table_name='production')
    op.drop_table('production')
    op.drop_index(op.f('ix_contacts_phone'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_index(op.f('ix_companies_tax_id'), table_name='companies')
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_index(op.f('ix_companies_legal_name'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_index(op.f('ix_companies_email'), table_name='companies')
    op.drop_table('companies')
    # ### end Alembic commands ###
