"""Add NotionLink and NotionNoteCache tables

Revision ID: notion_tables
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'notion_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create notion_links table
    op.create_table('notion_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(length=255), nullable=False),
        sa.Column('workspace_name', sa.String(length=255), nullable=True),
        sa.Column('workspace_icon', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create notion_note_cache table
    op.create_table('notion_note_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
        sa.Column('last_edited_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('page_id')
    )
    op.create_index(op.f('ix_notion_note_cache_last_edited_time'), 'notion_note_cache', ['last_edited_time'], unique=False)
    op.create_index(op.f('ix_notion_note_cache_user_id'), 'notion_note_cache', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notion_note_cache_user_id'), table_name='notion_note_cache')
    op.drop_index(op.f('ix_notion_note_cache_last_edited_time'), table_name='notion_note_cache')
    op.drop_table('notion_note_cache')
    op.drop_table('notion_links')
