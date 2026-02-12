import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, get_redis
from app.models.generation_job import GenerationJob
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    GenerationJobRead,
    PortfolioCreate,
    PortfolioPreviewResponse,
    PortfolioRead,
    PortfolioUpdate,
)
from app.services.events import generation_event_stream
from app.tasks.generation import generate_portfolio
from app.utils.helpers import utcnow
from app.utils.metrics import GENERATION_JOBS_TOTAL

router = APIRouter()


async def _get_portfolio_or_404(
    db: AsyncSession,
    portfolio_id: str,
    user_id: uuid.UUID,
) -> Portfolio:
    portfolio = await db.scalar(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
    )
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.get("", response_model=list[PortfolioRead])
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PortfolioRead]:
    result = await db.scalars(select(Portfolio).where(Portfolio.user_id == current_user.id))
    return [PortfolioRead.model_validate(item) for item in result.all()]


@router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioRead:
    portfolio = Portfolio(
        user_id=current_user.id,
        subdomain=payload.subdomain,
        template_id=payload.template_id,
        theme_config=payload.theme_config,
    )
    db.add(portfolio)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Subdomain already exists") from exc

    await db.refresh(portfolio)
    return PortfolioRead.model_validate(portfolio)


@router.get("/{portfolio_id}", response_model=PortfolioRead)
async def get_portfolio(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioRead:
    portfolio = await _get_portfolio_or_404(db, portfolio_id, current_user.id)
    return PortfolioRead.model_validate(portfolio)


@router.patch("/{portfolio_id}", response_model=PortfolioRead)
async def update_portfolio(
    portfolio_id: str,
    payload: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioRead:
    portfolio = await _get_portfolio_or_404(db, portfolio_id, current_user.id)
    if payload.custom_domain is not None:
        portfolio.custom_domain = payload.custom_domain
    if payload.template_id is not None:
        portfolio.template_id = payload.template_id
    if payload.theme_config is not None:
        portfolio.theme_config = payload.theme_config
    if payload.is_published is not None:
        portfolio.is_published = payload.is_published

    await db.commit()
    await db.refresh(portfolio)
    return PortfolioRead.model_validate(portfolio)


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    portfolio = await _get_portfolio_or_404(db, portfolio_id, current_user.id)
    await db.delete(portfolio)
    await db.commit()
    return {"status": "deleted"}


@router.post("/{portfolio_id}/generate", response_model=GenerationJobRead)
async def trigger_generation(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GenerationJobRead:
    portfolio = await _get_portfolio_or_404(db, portfolio_id, current_user.id)
    job = GenerationJob(
        user_id=current_user.id,
        portfolio_id=portfolio.id,
        status="pending",
        progress_percentage=0,
        current_step="Queued",
        started_at=utcnow(),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    generate_portfolio.delay(str(job.id))
    GENERATION_JOBS_TOTAL.labels(status="queued").inc()
    return GenerationJobRead.model_validate(job)


@router.get("/{portfolio_id}/preview", response_model=PortfolioPreviewResponse)
async def preview_portfolio(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PortfolioPreviewResponse:
    portfolio = await _get_portfolio_or_404(db, portfolio_id, current_user.id)
    html = portfolio.generated_html or "<html><body><h1>Portfolio not generated yet.</h1></body></html>"
    return PortfolioPreviewResponse(portfolio_id=portfolio_id, html=html)


@router.get("/{portfolio_id}/events")
async def stream_generation_events(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
    job_id: str | None = Query(default=None),
):
    await _get_portfolio_or_404(db, portfolio_id, current_user.id)

    if job_id is None:
        latest_job = await db.scalar(
            select(GenerationJob)
            .where(GenerationJob.portfolio_id == portfolio_id)
            .order_by(GenerationJob.started_at.desc())
            .limit(1)
        )
        if latest_job is None:
            raise HTTPException(status_code=404, detail="No generation jobs found")
        job_id = str(latest_job.id)

    async def event_generator():
        async for event in generation_event_stream(redis, job_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
