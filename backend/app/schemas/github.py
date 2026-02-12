from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GitHubProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    bio: str | None = None
    location: str | None = None
    company: str | None = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    total_stars: int = 0
    synced_at: datetime | None = None


class RepositoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    github_id: int
    name: str
    full_name: str
    description: str | None = None
    ai_description: str | None = None
    url: str
    language: str | None = None
    languages: dict = {}
    topics: list = []
    stars: int = 0
    forks: int = 0
    pushed_at: datetime | None = None


class SyncStatusResponse(BaseModel):
    status: str
    detail: str
