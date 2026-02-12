from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    subdomain: str = Field(min_length=3, max_length=63)
    template_id: str = "minimal"
    theme_config: dict = {}


class PortfolioUpdate(BaseModel):
    custom_domain: str | None = None
    template_id: str | None = None
    theme_config: dict | None = None
    is_published: bool | None = None


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    subdomain: str
    custom_domain: str | None = None
    template_id: str
    theme_config: dict
    is_published: bool
    last_generated_at: datetime | None = None
    view_count: int
    created_at: datetime
    updated_at: datetime


class GenerationJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    portfolio_id: str
    status: str
    progress_percentage: int
    current_step: str | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class PortfolioPreviewResponse(BaseModel):
    portfolio_id: str
    html: str
