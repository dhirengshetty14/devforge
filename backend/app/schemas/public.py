from pydantic import BaseModel, Field


class PublicGenerateRequest(BaseModel):
    github_url: str = Field(min_length=1, max_length=512)
    template_id: str = Field(default="minimal", min_length=1, max_length=100)


class PublicGenerateResponse(BaseModel):
    username: str
    portfolio_path: str
    portfolio_url: str
    projects_analyzed: int
    summary: str
