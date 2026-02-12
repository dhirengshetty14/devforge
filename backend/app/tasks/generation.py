from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis_client
from app.models.generation_job import GenerationJob
from app.models.portfolio import Portfolio
from app.models.repository import Repository
from app.models.skill import Skill
from app.models.user import User
from app.services.deployer import DeployerService
from app.services.events import publish_generation_event
from app.tasks.ai_tasks import generate_project_description
from app.tasks.analysis import analyze_repository
from app.tasks.celery_app import celery_app
from app.utils.helpers import utcnow

settings = get_settings()


def _render_basic_portfolio(
    username: str,
    subdomain: str,
    template_id: str,
    theme: dict,
    repositories: list[Repository],
    skills: list[Skill],
) -> str:
    accent = theme.get("accent", "#0f766e")
    font = theme.get("font", "system-ui, sans-serif")
    repo_cards = []
    for repo in repositories:
        desc = repo.ai_description or repo.description or "No description available."
        repo_cards.append(
            f"""
            <article class="card">
              <h3>{repo.name}</h3>
              <p>{desc}</p>
              <div class="meta">
                <span>Stars: {repo.stars}</span>
                <span>Forks: {repo.forks}</span>
                <a href="{repo.url}" target="_blank" rel="noreferrer">Source</a>
              </div>
            </article>
            """
        )
    skill_tags = " ".join(
        [
            f'<span class="skill">{skill.name} ({skill.proficiency}/5)</span>'
            for skill in skills[:30]
        ]
    )
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{username} | DevForge Portfolio</title>
  <style>
    :root {{
      --accent: {accent};
      --font: {font};
      --bg: #f6f8fb;
      --fg: #0f172a;
      --card: #ffffff;
      --muted: #475569;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--font);
      color: var(--fg);
      background:
        radial-gradient(circle at 10% 10%, #dbeafe 0, transparent 35%),
        radial-gradient(circle at 90% 90%, #cffafe 0, transparent 40%),
        var(--bg);
    }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem 4rem; }}
    .hero {{
      display: grid;
      gap: 0.5rem;
      margin-bottom: 2rem;
      padding: 1.5rem;
      border-radius: 16px;
      background: linear-gradient(135deg, #ffffff, #eff6ff);
      border: 1px solid #e2e8f0;
    }}
    .badge {{
      display: inline-block;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent) 14%, white);
      color: #0f172a;
      font-size: 0.8rem;
      width: fit-content;
    }}
    h1 {{ margin: 0; font-size: clamp(2rem, 4vw, 3rem); }}
    p {{ color: var(--muted); }}
    .skills {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin: 1rem 0 2rem;
    }}
    .skill {{
      padding: 0.35rem 0.7rem;
      border: 1px solid #cbd5e1;
      border-radius: 999px;
      background: #fff;
      font-size: 0.8rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1rem;
    }}
    .card {{
      background: var(--card);
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 1rem;
      box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
    }}
    .card h3 {{ margin-top: 0; margin-bottom: 0.5rem; }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 0.75rem;
      font-size: 0.85rem;
    }}
    .meta a {{ color: var(--accent); text-decoration: none; }}
    @media (max-width: 640px) {{
      main {{ padding: 1rem 0.75rem 3rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <span class="badge">DevForge • {template_id}</span>
      <h1>{username}</h1>
      <p>AI-enhanced engineering portfolio hosted at {subdomain}.devforge.dev</p>
    </section>
    <section>
      <h2>Core Skills</h2>
      <div class="skills">{skill_tags or "<span class='skill'>No skills extracted yet</span>"}</div>
    </section>
    <section>
      <h2>Projects</h2>
      <div class="grid">{''.join(repo_cards) or "<p>No repositories synced yet.</p>"}</div>
    </section>
  </main>
</body>
</html>
"""


async def _update_job(
    job_id: uuid.UUID,
    status: str,
    progress: int,
    step: str,
    error_message: str | None = None,
    completed: bool = False,
) -> GenerationJob:
    async with AsyncSessionLocal() as db:
        job = await db.scalar(select(GenerationJob).where(GenerationJob.id == job_id))
        if job is None:
            raise ValueError("Generation job not found")
        job.status = status
        job.progress_percentage = progress
        job.current_step = step
        job.error_message = error_message
        if completed:
            job.completed_at = utcnow()
        await db.commit()
        await db.refresh(job)
        return job


async def _emit(job_id: str, payload: dict) -> None:
    redis = get_redis_client()
    await publish_generation_event(redis, job_id, payload)


@celery_app.task(bind=True, max_retries=settings.celery_max_retries)
def generate_portfolio(self, generation_job_id: str) -> dict:
    async def _run() -> dict:
        job_uuid = uuid.UUID(generation_job_id)

        await _update_job(job_uuid, status="processing", progress=5, step="Starting generation")
        await _emit(
            generation_job_id,
            {"job_id": generation_job_id, "status": "processing", "progress": 5, "step": "Starting generation"},
        )

        async with AsyncSessionLocal() as db:
            job = await db.scalar(select(GenerationJob).where(GenerationJob.id == job_uuid))
            if job is None:
                raise ValueError("Generation job not found")
            portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == job.portfolio_id))
            if portfolio is None:
                raise ValueError("Portfolio not found")

            repos = (
                await db.scalars(
                    select(Repository)
                    .where(Repository.user_id == portfolio.user_id)
                    .order_by(Repository.stars.desc())
                    .limit(20)
                )
            ).all()
            skills = (
                await db.scalars(
                    select(Skill).where(Skill.user_id == portfolio.user_id).order_by(Skill.proficiency.desc())
                )
            ).all()
            user = await db.scalar(select(User).where(User.id == job.user_id))
            username = user.github_username if user else "Developer"

        await _update_job(job_uuid, status="processing", progress=20, step="Analyzing repositories")
        await _emit(
            generation_job_id,
            {
                "job_id": generation_job_id,
                "status": "processing",
                "progress": 20,
                "step": f"Analyzing repositories (0/{len(repos)})",
            },
        )

        for index, repo in enumerate(repos, start=1):
            analyze_repository.delay(str(repo.id))
            await _emit(
                generation_job_id,
                {
                    "job_id": generation_job_id,
                    "status": "processing",
                    "progress": min(45, 20 + int(index / max(len(repos), 1) * 25)),
                    "step": f"Analyzing repositories ({index}/{len(repos)})",
                },
            )

        await _update_job(job_uuid, status="processing", progress=50, step="Generating AI descriptions")
        await _emit(
            generation_job_id,
            {"job_id": generation_job_id, "status": "processing", "progress": 50, "step": "Generating AI descriptions"},
        )

        for index, repo in enumerate(repos, start=1):
            generate_project_description.delay(str(repo.id))
            await _emit(
                generation_job_id,
                {
                    "job_id": generation_job_id,
                    "status": "processing",
                    "progress": min(75, 50 + int(index / max(len(repos), 1) * 25)),
                    "step": f"Generating descriptions ({index}/{len(repos)})",
                },
            )

        # Reload data to capture updates committed by above task triggers.
        async with AsyncSessionLocal() as db:
            job = await db.scalar(select(GenerationJob).where(GenerationJob.id == job_uuid))
            if job is None:
                raise ValueError("Generation job missing")
            portfolio = await db.scalar(select(Portfolio).where(Portfolio.id == job.portfolio_id))
            if portfolio is None:
                raise ValueError("Portfolio missing")
            repos = (
                await db.scalars(
                    select(Repository)
                    .where(Repository.user_id == portfolio.user_id)
                    .order_by(Repository.stars.desc())
                    .limit(20)
                )
            ).all()
            skills = (
                await db.scalars(
                    select(Skill).where(Skill.user_id == portfolio.user_id).order_by(Skill.proficiency.desc())
                )
            ).all()
            user = await db.scalar(select(User).where(User.id == job.user_id))
            username = user.github_username if user else "Developer"

            html = _render_basic_portfolio(
                username=username,
                subdomain=portfolio.subdomain,
                template_id=portfolio.template_id,
                theme=portfolio.theme_config or {},
                repositories=repos,
                skills=skills,
            )

            deployer = DeployerService()
            deployed_path = deployer.deploy_static_portfolio(portfolio.subdomain, html)

            portfolio.generated_html = html
            portfolio.last_generated_at = utcnow()
            await db.commit()

        await _update_job(job_uuid, status="completed", progress=100, step="Completed", completed=True)
        await _emit(
            generation_job_id,
            {
                "job_id": generation_job_id,
                "status": "completed",
                "progress": 100,
                "step": "Completed",
                "url": deployed_path,
            },
        )
        return {"job_id": generation_job_id, "status": "completed", "url": deployed_path}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        try:
            asyncio.run(
                _update_job(
                    uuid.UUID(generation_job_id),
                    status="failed",
                    progress=100,
                    step="Failed",
                    error_message=str(exc),
                    completed=True,
                )
            )
            asyncio.run(
                _emit(
                    generation_job_id,
                    {"job_id": generation_job_id, "status": "failed", "progress": 100, "step": "Failed", "error": str(exc)},
                )
            )
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
