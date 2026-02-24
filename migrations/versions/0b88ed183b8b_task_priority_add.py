"""task priority add

Revision ID: 0b88ed183b8b
Revises: e6abe9526008
Create Date: 2026-02-22 21:50:18.229076

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b88ed183b8b"
down_revision: Union[str, Sequence[str], None] = "e6abe9526008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the Enum type explicitly
    task_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="taskpriority")
    task_priority.create(op.get_bind())

    # Add the column using the newly created type with a server default
    op.add_column(
        "tasks",
        sa.Column("priority", task_priority, nullable=False, server_default="LOW"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the column first
    op.drop_column("tasks", "priority")

    # Then drop the Enum type
    task_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="taskpriority")
    task_priority.drop(op.get_bind())
