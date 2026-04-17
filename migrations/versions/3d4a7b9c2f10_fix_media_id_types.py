"""fix media id types

Revision ID: 3d4a7b9c2f10
Revises: 01be7f76e26d
Create Date: 2026-04-17 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d4a7b9c2f10"
down_revision = "01be7f76e26d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("medias", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.BIGINT(),
            type_=sa.Integer(),
            existing_nullable=False,
            autoincrement=True,
        )
        batch_op.alter_column(
            "user_id",
            existing_type=sa.BIGINT(),
            type_=sa.Integer(),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("medias", schema=None) as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            type_=sa.BIGINT(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "id",
            existing_type=sa.Integer(),
            type_=sa.BIGINT(),
            existing_nullable=False,
            autoincrement=True,
        )
