from sqlalchemy import BigInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("github_id", name="uq_users_github_id"),
        UniqueConstraint("github_username", name="uq_users_github_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    github_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    github_username: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    github_profile = relationship(
        "GitHubProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    repositories = relationship("Repository", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="user", cascade="all, delete-orphan")
