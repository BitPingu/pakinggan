"""add artist relationship to tracks.

Revision ID: ed6b64b1350b
Revises: 89f34b0f84e9
Create Date: 2026-11-25 16:10:06.296687
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Revision identifiers used by Alembic.
revision: str = "ed6b64b1350b"
down_revision: str | Sequence[str] | None = "89f34b0f84e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adds the artist ID column as nullable initially.
    op.add_column(
        "tracks",
        sa.Column("artist_id", sa.Integer(), nullable=True),
    )

    # Populates each track's artist ID using its associated album.
    op.execute(
        """
        UPDATE tracks
        SET artist_id = albums.artist_id
        FROM albums
        WHERE tracks.album_id = albums.id
        """
    )

    # Creates the foreign key to the artists table.
    op.create_foreign_key(
        "fk_tracks_artist_id_artists",
        "tracks",
        "artists",
        ["artist_id"],
        ["id"],
    )

    # Requires every track to have an associated artist.
    op.alter_column(
        "tracks",
        "artist_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Removes the artist foreign key and column.
    op.drop_constraint(
        "fk_tracks_artist_id_artists",
        "tracks",
        type_="foreignkey",
    )
    op.drop_column("tracks", "artist_id")
