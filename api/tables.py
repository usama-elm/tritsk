from uuid import uuid4

from sqlalchemy import (
    UUID,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    SmallInteger,
    String,
    Table,
    Text,
)

tables_metadata = MetaData()

users = Table(
    "users",
    tables_metadata,
    Column("id", UUID, primary_key=True, key="id", default=uuid4),
    Column("username", String(200), key="username"),
    Column("name", String(200), key="name"),
    Column("aftername", String(200), key="aftername"),
    Column("mail", String(200), key="mail"),
    Column("password", String(200), key="password"),
)

priority = Table(
    "priority",
    tables_metadata,
    Column("id", BigInteger, primary_key=True, key="id"),
    Column("title", String(200), key="title"),
    Column("rank", SmallInteger, key="rank"),
    Column("description", Text, key="description"),
)

tasks = Table(
    "tasks",
    tables_metadata,
    Column("id", BigInteger, primary_key=True, key="id"),
    Column("title", String(200), key="title"),
    Column("content", Text, key="content"),
    Column(
        "date_creation",
        DateTime(timezone=True),
        key="date_creation",
    ),
    Column("priority_id", BigInteger, ForeignKey("priority.id"), key="priority_id"),
    Column("deadline", DateTime(timezone=True), key="deadline"),
)

projects = Table(
    "projects",
    tables_metadata,
    Column("id", BigInteger, primary_key=True, key="id"),
    Column("name", String(200), key="name"),
    Column("description", Text, key="description"),
)

project_user_rel = Table(
    "project_user_rel",
    tables_metadata,
    Column("id", BigInteger, primary_key=True, key="id"),
    Column("project_id", BigInteger, ForeignKey("projects.id"), key="project_id"),
    Column("user_id", UUID, ForeignKey("users.id"), key="user_id"),
    Column("role", String(50), key="role"),
)

task_user_rel = Table(
    "task_user_rel",
    tables_metadata,
    Column("task_id", BigInteger, ForeignKey("tasks.id"), key="task_id"),
    Column("project_id", BigInteger, ForeignKey("projects.id"), key="project_id"),
    Column("user_id", UUID, ForeignKey("users.id"), key="user_id"),
)
