from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

TEMPLATES = [
    {
        "id": "minimal",
        "name": "Minimal Pro",
        "description": "Clean engineering-focused template.",
        "defaults": {"accent": "#0f766e", "font": "Space Grotesk"},
    },
    {
        "id": "modern",
        "name": "Modern Grid",
        "description": "Balanced layout with metrics-first sections.",
        "defaults": {"accent": "#1d4ed8", "font": "Sora"},
    },
    {
        "id": "creative",
        "name": "Creative Systems",
        "description": "Bold visual narrative for senior portfolio storytelling.",
        "defaults": {"accent": "#ea580c", "font": "General Sans"},
    },
]


class TemplateCustomizePayload(BaseModel):
    theme_config: dict


@router.get("")
async def list_templates() -> list[dict]:
    return TEMPLATES


@router.get("/{template_id}")
async def get_template(template_id: str) -> dict:
    for template in TEMPLATES:
        if template["id"] == template_id:
            return template
    raise HTTPException(status_code=404, detail="Template not found")


@router.post("/{template_id}/customize")
async def customize_template(template_id: str, payload: TemplateCustomizePayload) -> dict:
    template = await get_template(template_id)
    return {
        "template_id": template["id"],
        "resolved_theme": {**template["defaults"], **payload.theme_config},
    }
