"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel
from backend.app import models

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.drop_all(bind=bind)
