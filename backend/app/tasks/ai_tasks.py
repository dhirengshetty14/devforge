from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.repository import Repository
from app.services.ai import AIService
from app.tasks.celery_app import celery_app

settings = get_settings()


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def generate_project_description(self, repository_id: str) -> dict:
    async def _run() -> dict:
        repo_uuid = uuid.UUID(repository_id)
        async with AsyncSessionLocal() as db:
            repo = await db.scalar(select(Repository).where(Repository.id == repo_uuid))
            if repo is None:
                raise ValueError("Repository not found")
            if repo.ai_description:
                return {"repository_id": repository_id, "cached": True}

            ai = AIService()
            description = await ai.generate_project_description(
                repo_name=repo.name,
                readme_excerpt=repo.description or "",
                languages=repo.languages or ({repo.language: 1} if repo.language else {}),
                commits_summary=f"stars={repo.stars}, forks={repo.forks}",
            )
            repo.ai_description = description
            await db.commit()
            return {"repository_id": repository_id, "cached": False}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
