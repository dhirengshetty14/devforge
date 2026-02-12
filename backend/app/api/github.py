from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, get_redis
from app.models.github_profile import GitHubProfile
from app.models.repository import Repository
from app.models.user import User
from app.schemas.github import GitHubProfileRead, RepositoryRead, SyncStatusResponse
from app.tasks.celery_app import celery_app
from app.tasks.github_sync import sync_user_github

router = APIRouter()


@router.post("/sync", response_model=SyncStatusResponse)
async def trigger_sync(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> SyncStatusResponse:
    task = sync_user_github.delay(str(current_user.id))
    await redis.setex(f"sync:user:{current_user.id}", 3600, task.id)
    return SyncStatusResponse(status="queued", detail=f"Task {task.id} queued")


@router.get("/sync/status", response_model=SyncStatusResponse)
async def sync_status(
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> SyncStatusResponse:
    task_id = await redis.get(f"sync:user:{current_user.id}")
    if not task_id:
        return SyncStatusResponse(status="idle", detail="No sync task found")

    async_result = celery_app.AsyncResult(task_id)
    state = async_result.state
    return SyncStatusResponse(status=state.lower(), detail=f"Task {task_id}: {state}")


@router.get("/profile", response_model=GitHubProfileRead)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GitHubProfileRead:
    profile = await db.scalar(select(GitHubProfile).where(GitHubProfile.user_id == current_user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not synced")
    return GitHubProfileRead.model_validate(profile)


@router.get("/repositories", response_model=list[RepositoryRead])
async def get_repositories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[RepositoryRead]:
    statement = (
        select(Repository)
        .where(Repository.user_id == current_user.id)
        .order_by(Repository.stars.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.scalars(statement)
    return [RepositoryRead.model_validate(repo) for repo in result.all()]


@router.get("/repos/{repo_id}", response_model=RepositoryRead)
async def get_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepositoryRead:
    repository = await db.scalar(
        select(Repository).where(Repository.id == repo_id, Repository.user_id == current_user.id)
    )
    if repository is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return RepositoryRead.model_validate(repository)
