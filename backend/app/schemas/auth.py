from pydantic import BaseModel, Field


class GitHubAuthURLResponse(BaseModel):
    authorization_url: str
    state: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    id: str
    github_username: str
    email: str | None = None
    avatar_url: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=10)
