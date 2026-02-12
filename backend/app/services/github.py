from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.core.exceptions import ExternalServiceUnavailable
from app.models.github_profile import GitHubProfile
from app.models.repository import Repository
from app.models.user import User
from app.services.rate_limiter import RateLimiter

settings = get_settings()

GITHUB_API_BASE = "https://api.github.com"
GITHUB_OAUTH_BASE = "https://github.com/login/oauth"


class GitHubAPIError(ExternalServiceUnavailable):
    pass


class GitHubService:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    def authorization_url(self, state: str) -> str:
        return (
            f"{GITHUB_OAUTH_BASE}/authorize"
            f"?client_id={settings.github_client_id}"
            f"&redirect_uri={settings.github_redirect_uri}"
            f"&scope=read:user user:email repo"
            f"&state={state}"
        )

    async def exchange_code_for_token(self, code: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{GITHUB_OAUTH_BASE}/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                    "redirect_uri": settings.github_redirect_uri,
                },
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            if not token:
                raise GitHubAPIError("GitHub OAuth token exchange failed")
            return token

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=16),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True,
    )
    async def _request(self, method: str, url: str, token: str, params: dict | None = None) -> Any:
        await self.rate_limiter.check_rate_limit("github:minute", settings.rate_limit_per_minute, 60)
        await self.rate_limiter.consume_token(
            "github:hour",
            capacity=settings.github_api_rate_limit,
            refill_rate_per_second=settings.github_api_rate_limit / 3600.0,
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, headers=self._headers(token), params=params)
        if response.status_code == 429:
            raise GitHubAPIError("GitHub API rate limit hit")
        if response.status_code >= 500:
            raise GitHubAPIError(f"GitHub API unavailable ({response.status_code})")
        response.raise_for_status()
        return response.json()

    async def get_authenticated_user(self, token: str) -> dict:
        return await self._request("GET", f"{GITHUB_API_BASE}/user", token)

    async def get_user_emails(self, token: str) -> list[dict]:
        data = await self._request("GET", f"{GITHUB_API_BASE}/user/emails", token)
        if isinstance(data, list):
            return data
        return []

    async def sync_profile(self, db: AsyncSession, user: User, token: str) -> GitHubProfile:
        payload = await self.get_authenticated_user(token)
        profile = await db.scalar(select(GitHubProfile).where(GitHubProfile.user_id == user.id))
        if profile is None:
            profile = GitHubProfile(user_id=user.id)
            db.add(profile)

        profile.name = payload.get("name")
        profile.bio = payload.get("bio")
        profile.location = payload.get("location")
        profile.company = payload.get("company")
        profile.blog_url = payload.get("blog")
        profile.twitter_username = payload.get("twitter_username")
        profile.public_repos = payload.get("public_repos") or 0
        profile.followers = payload.get("followers") or 0
        profile.following = payload.get("following") or 0
        profile.synced_at = datetime.utcnow()

        await db.flush()
        return profile

    async def sync_repositories(self, db: AsyncSession, user: User, token: str) -> int:
        repos_synced = 0
        page = 1
        per_page = 100
        while True:
            payload = await self._request(
                "GET",
                f"{GITHUB_API_BASE}/user/repos",
                token,
                params={"page": page, "per_page": per_page, "sort": "updated"},
            )
            if not isinstance(payload, list) or len(payload) == 0:
                break
            for repo_data in payload:
                repo = await db.scalar(
                    select(Repository).where(Repository.github_id == repo_data["id"])
                )
                if repo is None:
                    repo = Repository(
                        user_id=user.id,
                        github_id=repo_data["id"],
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        url=repo_data["html_url"],
                    )
                    db.add(repo)

                repo.name = repo_data["name"]
                repo.full_name = repo_data["full_name"]
                repo.description = repo_data.get("description")
                repo.url = repo_data["html_url"]
                repo.homepage = repo_data.get("homepage")
                repo.language = repo_data.get("language")
                repo.topics = repo_data.get("topics", [])
                repo.stars = repo_data.get("stargazers_count", 0)
                repo.forks = repo_data.get("forks_count", 0)
                repo.is_fork = repo_data.get("fork", False)
                repo.is_private = repo_data.get("private", False)
                pushed = repo_data.get("pushed_at")
                repo.pushed_at = datetime.fromisoformat(pushed.replace("Z", "+00:00")) if pushed else None
                repos_synced += 1

            page += 1
            if len(payload) < per_page:
                break
        return repos_synced

    async def fetch_repo_commits(
        self,
        token: str,
        owner: str,
        repo: str,
        per_page: int = 100,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits",
            token,
            params={"per_page": per_page, "page": page},
        )
        if isinstance(data, list):
            return data
        return []
