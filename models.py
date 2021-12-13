from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import Base

xref_table = Table(
    "user_project_xref", Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    google_subject = Column(String, unique=True)
    projects = relationship(lambda: Project, secondary=xref_table, backref="users")
    login_tokens = relationship(lambda: LoginToken, backref="user")


class LoginToken(Base):
    __tablename__ = "login_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id))


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    date_proposed = Column(DateTime)
    time = Column(DateTime)
    type = Column(String)
    description = Column(String)
    github = Column(String)
    url = Column(String)
