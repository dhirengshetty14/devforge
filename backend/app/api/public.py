from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, HTTPException, Request
from redis.asyncio import Redis

from app.core.redis import get_redis_client
from app.schemas.public import PublicGenerateRequest, PublicGenerateResponse
from app.services.deployer import DeployerService
from app.services.github import GitHubAPIError, GitHubService, parse_github_username
from app.services.public_portfolio import build_summary, describe_repo, extract_skills, render_public_portfolio
from app.services.rate_limiter import RateLimiter

router = APIRouter()


def _to_safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", value.strip().lower()).strip("-")
    return slug or "portfolio"


@router.post("/generate", response_model=PublicGenerateResponse)
async def public_generate_portfolio(
    payload: PublicGenerateRequest,
    request: Request,
) -> PublicGenerateResponse:
    try:
        username = parse_github_username(payload.github_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    redis: Redis = get_redis_client()
    github_service = GitHubService(RateLimiter(redis))

    try:
        profile = await github_service.get_public_user(username)
        repositories = await github_service.get_public_repositories(username, max_repos=120)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to fetch GitHub data") from exc

    filtered_repositories = [repo for repo in repositories if not repo.get("fork")]
    for repository in filtered_repositories:
        if not repository.get("description"):
            repository["description"] = describe_repo(repository)

    skills = extract_skills(filtered_repositories)
    summary = build_summary(profile, filtered_repositories, skills)

    html = render_public_portfolio(
        username=username,
        profile=profile,
        repositories=filtered_repositories,
        skills=skills,
        template_id=payload.template_id,
    )

    suffix = str(uuid.uuid4())[:8]
    slug = _to_safe_slug(f"{username}-{suffix}")
    deployer = DeployerService()
    portfolio_path = deployer.deploy_static_portfolio(slug, html)
    base_url = str(request.base_url).rstrip("/")
    portfolio_url = f"{base_url}{portfolio_path}"

    return PublicGenerateResponse(
        username=username,
        portfolio_path=portfolio_path,
        portfolio_url=portfolio_url,
        projects_analyzed=len(filtered_repositories),
        summary=summary,
    )
