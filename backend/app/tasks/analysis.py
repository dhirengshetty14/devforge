from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

from celery import chord, group
from sqlalchemy import delete, select

from app.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis_client
from app.core.security import decrypt_token
from app.models.commit import Commit
from app.models.repository import Repository
from app.models.skill import Skill
from app.models.user import User
from app.services.github import GitHubService
from app.services.rate_limiter import RateLimiter
from app.tasks.celery_app import celery_app
from app.utils.helpers import utcnow

settings = get_settings()


def _parse_owner_repo(full_name: str) -> tuple[str, str]:
    parts = full_name.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repository full_name: {full_name}")
    return parts[0], parts[1]


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def analyze_repository(self, repository_id: str) -> dict:
    async def _run() -> dict:
        repo_uuid = uuid.UUID(repository_id)
        async with AsyncSessionLocal() as db:
            repo = await db.scalar(select(Repository).where(Repository.id == repo_uuid))
            if repo is None:
                raise ValueError("Repository not found")

            user = await db.scalar(select(User).where(User.id == repo.user_id))
            if user is None or not user.access_token:
                raise ValueError("Repository owner token unavailable")
            token = decrypt_token(user.access_token)

            owner, repo_name = _parse_owner_repo(repo.full_name)
            github = GitHubService(RateLimiter(get_redis_client()))

            # Incremental update: only fetch recent commits and skip known SHAs.
            commits = await github.fetch_repo_commits(token, owner, repo_name, per_page=100, page=1)
            existing_shas = {
                sha
                for sha in (
                    await db.scalars(
                        select(Commit.sha).where(Commit.repository_id == repo.id).limit(5000)
                    )
                ).all()
            }
            new_commits = [item for item in commits if item.get("sha") not in existing_shas]
            shas = [item.get("sha") for item in new_commits if item.get("sha")]
            if not shas:
                repo.analyzed_at = utcnow()
                await db.commit()
                return {"repository_id": repository_id, "new_commits": 0, "batched": 0}

        # partition into batches of 100 and analyze in parallel via chord
        batches = [shas[i : i + 100] for i in range(0, len(shas), 100)]
        job = group([analyze_commits_batch.s(repository_id, batch) for batch in batches])
        result = chord(job)(aggregate_commit_analysis.s(repository_id))
        return result.get(timeout=120)

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def analyze_commits_batch(self, repository_id: str, commit_shas: list[str]) -> dict:
    async def _run() -> dict:
        repo_uuid = uuid.UUID(repository_id)
        async with AsyncSessionLocal() as db:
            repo = await db.scalar(select(Repository).where(Repository.id == repo_uuid))
            if repo is None:
                raise ValueError("Repository not found")
            user = await db.scalar(select(User).where(User.id == repo.user_id))
            if user is None or not user.access_token:
                raise ValueError("Repository owner token unavailable")
            token = decrypt_token(user.access_token)
            owner, repo_name = _parse_owner_repo(repo.full_name)
            github = GitHubService(RateLimiter(get_redis_client()))

            inserted = 0
            existing = {
                sha
                for sha in (
                    await db.scalars(
                        select(Commit.sha).where(Commit.sha.in_(commit_shas))
                    )
                ).all()
            }
            for sha in commit_shas:
                if sha in existing:
                    continue
                # Use commit endpoint for detailed stats
                detail = await github.fetch_commit_detail(token, owner, repo_name, sha)
                commit_data = detail.get("commit", {})
                author = commit_data.get("author") or {}
                stats = detail.get("stats") or {}
                files = detail.get("files") or []

                committed_at_raw = author.get("date")
                committed_at = (
                    datetime.fromisoformat(committed_at_raw.replace("Z", "+00:00"))
                    if committed_at_raw
                    else utcnow()
                )

                commit = Commit(
                    repository_id=repo.id,
                    sha=sha,
                    message=commit_data.get("message", ""),
                    author_name=(author.get("name") or "")[:255] or None,
                    author_email=(author.get("email") or "")[:255] or None,
                    committed_at=committed_at,
                    additions=int(stats.get("additions") or 0),
                    deletions=int(stats.get("deletions") or 0),
                    files_changed=len(files),
                )
                db.add(commit)
                inserted += 1

            await db.commit()
            return {
                "repository_id": repository_id,
                "processed": len(commit_shas),
                "inserted": inserted,
                "additions": 0,
                "deletions": 0,
                "files_changed": 0,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task
def aggregate_commit_analysis(batch_results: list[dict], repository_id: str) -> dict:
    async def _run() -> dict:
        total_processed = 0
        total_inserted = 0
        for item in batch_results:
            total_processed += int(item.get("processed", 0))
            total_inserted += int(item.get("inserted", 0))

        async with AsyncSessionLocal() as db:
            repo = await db.scalar(select(Repository).where(Repository.id == uuid.UUID(repository_id)))
            if repo:
                repo.analyzed_at = utcnow()
                await db.commit()
        return {
            "repository_id": repository_id,
            "processed": total_processed,
            "inserted": total_inserted,
        }

    return asyncio.run(_run())


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def extract_skills(self, user_id: str) -> dict:
    async def _run() -> dict:
        user_uuid = uuid.UUID(user_id)
        async with AsyncSessionLocal() as db:
            user = await db.scalar(select(User).where(User.id == user_uuid))
            if user is None:
                raise ValueError("User not found")

            repos = (
                await db.scalars(select(Repository).where(Repository.user_id == user.id))
            ).all()
            language_usage: dict[str, int] = {}
            for repo in repos:
                languages = repo.languages or {}
                if not languages and repo.language:
                    languages = {repo.language: 1}
                for name, value in languages.items():
                    language_usage[name] = language_usage.get(name, 0) + int(value or 0)

            await db.execute(delete(Skill).where(Skill.user_id == user.id))

            for name, score in sorted(language_usage.items(), key=lambda x: x[1], reverse=True):
                proficiency = 5 if score > 10000 else 4 if score > 3000 else 3 if score > 1000 else 2
                db.add(
                    Skill(
                        user_id=user.id,
                        name=name,
                        category="language",
                        proficiency=proficiency,
                        usage_count=score,
                        last_used_at=utcnow(),
                    )
                )
            await db.commit()
            return {"user_id": user_id, "skills": len(language_usage)}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
