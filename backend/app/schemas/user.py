from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    github_id: int
    github_username: str
    email: str | None = None
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    email: str | None = None
