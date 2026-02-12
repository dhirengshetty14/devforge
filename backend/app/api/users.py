from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=str(current_user.id),
        github_id=current_user.github_id,
        github_username=current_user.github_username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
    )


@router.patch("/me", response_model=UserRead)
async def patch_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    if payload.email is not None:
        current_user.email = payload.email
    await db.commit()
    await db.refresh(current_user)
    return UserRead(
        id=str(current_user.id),
        github_id=current_user.github_id,
        github_username=current_user.github_username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
    )


@router.delete("/me")
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(current_user)
    await db.commit()
    return {"status": "deleted"}
