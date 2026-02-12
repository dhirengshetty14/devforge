from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


class AIService:
    async def generate_project_description(
        self,
        repo_name: str,
        readme_excerpt: str,
        languages: dict,
        commits_summary: str,
    ) -> str:
        prompt = (
            "Write a concise, recruiter-friendly 2-3 sentence description for a software project.\n"
            f"Project: {repo_name}\n"
            f"Languages: {languages}\n"
            f"README excerpt: {readme_excerpt[:1200]}\n"
            f"Commit summary: {commits_summary[:1200]}\n"
            "Focus on impact, architecture, and engineering quality."
        )

        if settings.groq_api_key:
            text = await self._call_groq(prompt)
            if text:
                return text

        if settings.openai_api_key:
            text = await self._call_openai(prompt)
            if text:
                return text

        return (
            f"{repo_name} is a production-focused project with a strong engineering foundation. "
            "It demonstrates practical system design, maintainable architecture, and consistent delivery quality."
        )

    async def _call_groq(self, prompt: str) -> str | None:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
        payload = {
            "model": settings.groq_model,
            "messages": [
                {"role": "system", "content": "You are a senior engineering writer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                return None
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_openai(self, prompt: str) -> str | None:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": "You are a senior engineering writer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                return None
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
