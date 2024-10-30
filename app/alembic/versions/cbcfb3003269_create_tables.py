"""Create tables

Revision ID: cbcfb3003269
Revises:
Create Date: 2024-10-11 17:45:55.014948

"""
from typing import Union

import sqlalchemy as sa

import os
from collections.abc import Sequence

import scripts

from alembic import op  # type: ignore
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession



# revision identifiers, used by Alembic.
revision: str = 'cbcfb3003269'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_USERNAME = os.getenv("ADMIN_USEREMAIL", "admin@adm.in")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Password_admin")


async def create_admin_user(
    conn: AsyncConnection,
    username: str,
    password: str,
) -> None:
    session = AsyncSession(bind=conn)
    await scripts.create_admin_user(session, username, password,)


async def create_user_role(conn: AsyncConnection) -> None:
    session = AsyncSession(bind=conn)
    await scripts.create_user_role(session)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "right",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("write", sa.Boolean(), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("only_own", sa.Boolean(), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.CheckConstraint(
            "model in ('user', 'file', 'token', 'role', 'right')",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model", "write", "read", "only_own"),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "file_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=70), nullable=False),
        sa.Column("first_name", sa.String(length=50)),
        sa.Column("last_name", sa.String(length=50)),
        sa.Column(
            "registration_time",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "role_right_relation",
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("right_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["right_id"], ["right.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
    )
    op.create_index(
        op.f("ix_role_right_relation_right_id"),
        "role_right_relation",
        ["right_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_role_right_relation_role_id"),
        "role_right_relation",
        ["role_id"],
        unique=False,
    )
    op.create_table(
        "file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("important", sa.Boolean(), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column(
            "start_time",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finish_time", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["file_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "token",
            sa.UUID(),
            server_default=sa.text(
                "gen_random_uuid()",
            ),
            nullable=False,
        ),
        sa.Column(
            "creation_time",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["file_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_table(
        "user_role_relation",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["file_user.id"]),
    )
    op.create_index(
        op.f("ix_user_role_relation_role_id"),
        "user_role_relation",
        ["role_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_role_relation_user_id"),
        "user_role_relation",
        ["user_id"],
        unique=False,
    )
    # ### end Alembic commands ###
    op.run_async(
        create_admin_user,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )
    op.run_async(create_user_role)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_user_role_relation_user_id"),
        table_name="user_role_relation",
    )
    op.drop_index(
        op.f("ix_user_role_relation_role_id"),
        table_name="user_role_relation",
    )
    op.drop_table("user_role_relation")
    op.drop_table("token")
    op.drop_table("file")
    op.drop_index(
        op.f("ix_role_right_relation_role_id"),
        table_name="role_right_relation",
    )
    op.drop_index(
        op.f("ix_role_right_relation_right_id"),
        table_name="role_right_relation",
    )
    op.drop_table("role_right_relation")
    op.drop_table("file_user")
    op.drop_table("role")
    op.drop_table("right")
    # ### end Alembic commands ###

# docker exec -it <container-id> psql -U app -d postgres -c "DROP DATABASE app;"
# docker exec -it <container-id> psql -U app -d postgres -c "CREATE DATABASE app;"