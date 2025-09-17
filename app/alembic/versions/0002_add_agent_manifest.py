"""Add agent manifest table

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-27 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_manifests table
    op.create_table('agent_manifests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('core_function', sa.Text(), nullable=True),
        sa.Column('key_capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mcp_command', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_manifests_agent_id'), 'agent_manifests', ['agent_id'], unique=True)
    op.create_index(op.f('ix_agent_manifests_status'), 'agent_manifests', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_manifests_status'), table_name='agent_manifests')
    op.drop_index(op.f('ix_agent_manifests_agent_id'), table_name='agent_manifests')
    op.drop_table('agent_manifests')