"""document ingestion hash, status, unique per owner, HNSW on embeddings

Revision ID: e7a1b2c3hash
Revises: c3a9012phase5
Create Date: 2026-04-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7a1b2c3hash"
down_revision: Union[str, Sequence[str], None] = "c3a9012phase5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("content_hash", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("ingestion_status", sa.Text(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("ingestion_error", sa.Text(), nullable=True),
    )
    op.execute(
        sa.text(
            "UPDATE documents SET content_hash = 'legacy-' || replace(id::text, '-', ''), "
            "ingestion_status = 'ready' "
            "WHERE content_hash IS NULL OR ingestion_status IS NULL"
        )
    )
    op.alter_column(
        "documents",
        "ingestion_status",
        nullable=False,
        server_default=sa.text("'pending'"),
    )
    op.alter_column("documents", "content_hash", nullable=False)
    op.create_unique_constraint(
        "uq_documents_owner_content_hash",
        "documents",
        ["owner_id", "content_hash"],
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
            "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw"))
    op.drop_constraint("uq_documents_owner_content_hash", "documents", type_="unique")
    op.drop_column("documents", "ingestion_error")
    op.drop_column("documents", "ingestion_status")
    op.drop_column("documents", "content_hash")
