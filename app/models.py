from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

project_technologies = Table(
    "project_technologies",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("technology_id", ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True),
)


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    projects: Mapped[list[Project]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", order_by="Project.id"
    )


class Technology(Base):
    __tablename__ = "technologies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(300))
    projects: Mapped[list[Project]] = relationship(
        secondary=project_technologies, back_populates="technologies"
    )


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    repository_url: Mapped[str | None] = mapped_column(String(500))
    demo_url: Mapped[str | None] = mapped_column(String(500))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), index=True)
    profile: Mapped[Profile] = relationship(back_populates="projects")
    technologies: Mapped[list[Technology]] = relationship(
        secondary=project_technologies, back_populates="projects"
    )
    feedbacks: Mapped[list[Feedback]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Feedback.id"
    )


class Feedback(Base):
    __tablename__ = "feedbacks"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(120), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project: Mapped[Project] = relationship(back_populates="feedbacks")
