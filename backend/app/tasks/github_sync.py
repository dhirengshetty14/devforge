from __future__ import annotations

import asyncio
import uuid
from typing import Any

from celery import chain
from sqlalchemy import select

from app.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis_client
from app.core.security import decrypt_token
from app.models.user import User
from app.services.github import GitHubService
from app.services.rate_limiter import RateLimiter
from app.tasks.analysis import extract_skills
from app.tasks.celery_app import celery_app

settings = get_settings()


async def _load_user_and_token(user_id: str) -> tuple[User, str]:
    user_uuid = uuid.UUID(user_id)
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.id == user_uuid))
        if user is None:
            raise ValueError("User not found")
        if not user.access_token:
            raise ValueError("User has no GitHub access token")
        return user, decrypt_token(user.access_token)


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def sync_github_profile(self, user_id: str) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        user, token = await _load_user_and_token(user_id)
        redis = get_redis_client()
        github_service = GitHubService(RateLimiter(redis))
        async with AsyncSessionLocal() as db:
            # Reload user in this session
            db_user = await db.scalar(select(User).where(User.id == user.id))
            profile = await github_service.sync_profile(db, db_user, token)
            await db.commit()
            return {"user_id": user_id, "profile_synced": True, "profile_id": str(profile.id)}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def sync_repositories(self, user_id: str) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        user, token = await _load_user_and_token(user_id)
        redis = get_redis_client()
        github_service = GitHubService(RateLimiter(redis))
        async with AsyncSessionLocal() as db:
            db_user = await db.scalar(select(User).where(User.id == user.id))
            count = await github_service.sync_repositories(db, db_user, token)
            await db.commit()
            return {"user_id": user_id, "repositories_synced": count}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def sync_user_github(self, user_id: str) -> dict[str, Any]:
    try:
        workflow = chain(
            sync_github_profile.s(user_id),
            sync_repositories.si(user_id),
            extract_skills.si(user_id),
        )
        async_result = workflow.apply_async()
        return {"workflow_id": async_result.id, "status": "queued", "user_id": user_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
