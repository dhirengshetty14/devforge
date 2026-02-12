from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.analytics_event import AnalyticsEvent
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.analytics import AnalyticsTrackRequest

router = APIRouter()


def _anonymize_ip(ip_address: str | None) -> str | None:
    if not ip_address:
        return None
    if "." in ip_address:
        parts = ip_address.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    return ip_address


@router.post("/track")
async def track_event(
    payload: AnalyticsTrackRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    event = AnalyticsEvent(
        portfolio_id=payload.portfolio_id,
        event_type=payload.event_type,
        event_data=payload.event_data,
        ip_address=_anonymize_ip(request.client.host if request.client else None),
        user_agent=request.headers.get("user-agent"),
        referrer=payload.referrer,
        created_at=datetime.utcnow(),
    )
    db.add(event)
    await db.commit()
    return {"status": "tracked"}


@router.get("/{portfolio_id}")
async def get_analytics(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    portfolio = await db.scalar(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id)
    )
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    counts_result = await db.execute(
        select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .where(AnalyticsEvent.portfolio_id == portfolio_id)
        .group_by(AnalyticsEvent.event_type)
    )
    counts = {event_type: count for event_type, count in counts_result.all()}

    recent_result = await db.scalars(
        select(AnalyticsEvent)
        .where(AnalyticsEvent.portfolio_id == portfolio_id)
        .order_by(AnalyticsEvent.created_at.desc())
        .limit(100)
    )
    recent = [
        {
            "id": str(item.id),
            "event_type": item.event_type,
            "event_data": item.event_data,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in recent_result.all()
    ]
    return {"portfolio_id": portfolio_id, "counts": counts, "recent": recent}
