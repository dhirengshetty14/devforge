from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Portfolio(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "portfolios"
    __table_args__ = (
        UniqueConstraint("subdomain", name="uq_portfolios_subdomain"),
        UniqueConstraint("custom_domain", name="uq_portfolios_custom_domain"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    subdomain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    template_id: Mapped[str] = mapped_column(String(100), default="minimal")
    theme_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_generated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="portfolios")
    analytics_events = relationship("AnalyticsEvent", back_populates="portfolio", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="portfolio", cascade="all, delete-orphan")
