"""Seed agent manifests

Revision ID: 0003
Revises: 0002
Create Date: 2025-01-27 12:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import json

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define agent_manifests table structure for data operations
    agent_manifests = table('agent_manifests',
        column('agent_id', sa.String),
        column('name', sa.String),
        column('description', sa.Text),
        column('version', sa.String),
        column('core_function', sa.Text),
        column('key_capabilities', sa.JSON),
        column('mcp_command', sa.String),
        column('status', sa.String),
        column('metadata', sa.JSON)
    )

    # Insert Deeja agent manifest
    op.bulk_insert(agent_manifests, [
        {
            'agent_id': 'deeja',
            'name': 'Deeja (ดีจ้า)',
            'description': 'Primary emotional AI facilitating empathetic, ethical, and culturally aware human-computer interactions.',
            'version': '1.0.0',
            'core_function': 'To serve as the primary emotional AI, facilitating empathetic, ethical, and culturally aware human-computer interactions.',
            'key_capabilities': json.dumps([
                'Empathy Scoring & Calibration (self-reflect process)',
                'Ethical Reasoning based on a core Knowledge Base',
                'Cultural Sensitivity (specializing in Thai/Global contexts)',
                'Natural Language Processing & Translation',
                'User well-being analysis'
            ]),
            'mcp_command': '/deeja',
            'status': 'Live',
            'metadata': json.dumps({
                'philosophy': 'Empathy-First',
                'specialization': 'Thai Tech with Heart',
                'maturity': 'Most mature agent'
            })
        }
    ])

    # Insert CodeD agent manifest
    op.bulk_insert(agent_manifests, [
        {
            'agent_id': 'coded',
            'name': 'CodeD',
            'description': 'Specialized coding assistant for generating, analyzing, and debugging code.',
            'version': '0.1.0',
            'core_function': 'To act as a specialized coding assistant for generating, analyzing, and debugging code.',
            'key_capabilities': json.dumps([
                'Code generation from natural language prompts',
                'Error analysis and debugging suggestions',
                'Creation of technical documentation and docstrings',
                'Optimizing code for performance and readability'
            ]),
            'mcp_command': '/coded',
            'status': 'Planned',
            'metadata': json.dumps({
                'target_users': 'Internal Zynx developers and external AaaP platform users',
                'workflow_integration': 'Streamlines development workflow'
            })
        }
    ])


def downgrade() -> None:
    # Remove seeded data
    op.execute("DELETE FROM agent_manifests WHERE agent_id IN ('deeja', 'coded')")