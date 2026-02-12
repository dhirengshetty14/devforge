from fastapi import APIRouter

from app.api import analytics, auth, github, portfolios, templates, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
