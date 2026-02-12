from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_token
from app.dependencies import get_current_user, get_db, get_redis
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    AuthUserResponse,
    GitHubAuthURLResponse,
    RefreshTokenRequest,
)
from app.services.auth import AuthService
from app.services.github import GitHubService
from app.services.rate_limiter import RateLimiter

router = APIRouter()


@router.post("/github", response_model=GitHubAuthURLResponse)
async def github_auth_start(redis: Redis = Depends(get_redis)) -> GitHubAuthURLResponse:
    auth_service = AuthService()
    state = auth_service.generate_state()
    await redis.setex(f"oauth:state:{state}", 600, "1")

    github_service = GitHubService(rate_limiter=RateLimiter(redis))
    return GitHubAuthURLResponse(
        authorization_url=github_service.authorization_url(state),
        state=state,
    )


@router.get("/github/callback", response_model=AuthTokenResponse)
async def github_auth_callback(
    code: str = Query(..., min_length=5),
    state: str = Query(..., min_length=8),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> AuthTokenResponse:
    state_key = f"oauth:state:{state}"
    exists = await redis.get(state_key)
    if not exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
    await redis.delete(state_key)

    github_service = GitHubService(rate_limiter=RateLimiter(redis))
    token = await github_service.exchange_code_for_token(code)
    github_user = await github_service.get_authenticated_user(token)
    emails = await github_service.get_user_emails(token)

    email = github_user.get("email")
    if not email:
        email = next((item.get("email") for item in emails if item.get("primary")), None)

    user = await db.scalar(select(User).where(User.github_id == github_user["id"]))
    if user is None:
        user = User(
            github_id=github_user["id"],
            github_username=github_user["login"],
            email=email,
            avatar_url=github_user.get("avatar_url"),
            access_token=encrypt_token(token),
        )
        db.add(user)
    else:
        user.github_username = github_user["login"]
        user.email = email or user.email
        user.avatar_url = github_user.get("avatar_url")
        user.access_token = encrypt_token(token)

    await db.commit()
    await db.refresh(user)

    tokens = AuthService.create_tokens(str(user.id))
    return AuthTokenResponse(**tokens)


@router.post("/logout")
async def logout() -> dict:
    return {"status": "ok"}


@router.post("/refresh")
async def refresh_token(payload: RefreshTokenRequest) -> dict:
    access_token = AuthService.refresh_access_token(payload.refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AuthUserResponse)
async def me(current_user: User = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse(
        id=str(current_user.id),
        github_username=current_user.github_username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
    )
