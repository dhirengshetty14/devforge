from datetime import datetime

from pydantic import BaseModel


class AnalyticsTrackRequest(BaseModel):
    portfolio_id: str
    event_type: str
    event_data: dict = {}
    referrer: str | None = None


class AnalyticsEventRead(BaseModel):
    id: str
    portfolio_id: str
    event_type: str
    event_data: dict
    created_at: datetime
