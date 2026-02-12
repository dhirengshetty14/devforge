from __future__ import annotations

from collections import Counter


def describe_repo(repo: dict) -> str:
    language = repo.get("language") or "multi-language"
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    topics = repo.get("topics") or []
    topic_suffix = ""
    if topics:
        topic_suffix = f" Focuses on {', '.join(topics[:3])}."
    return (
        f"{repo.get('name')} is a {language} project with {stars} stars and {forks} forks. "
        f"It demonstrates practical engineering and maintainable implementation.{topic_suffix}"
    )


def extract_skills(repositories: list[dict]) -> list[dict]:
    language_counts: Counter[str] = Counter()
    for repo in repositories:
        language = repo.get("language")
        if language:
            language_counts[language] += 1

    skills = []
    for name, count in language_counts.most_common(20):
        proficiency = 5 if count >= 8 else 4 if count >= 5 else 3 if count >= 3 else 2
        skills.append(
            {
                "name": name,
                "category": "language",
                "proficiency": proficiency,
            }
        )
    return skills


def build_summary(profile: dict, repositories: list[dict], skills: list[dict]) -> str:
    total_repos = len(repositories)
    total_stars = sum(int(repo.get("stargazers_count") or 0) for repo in repositories)
    top_skills = ", ".join(skill["name"] for skill in skills[:4]) or "general software engineering"
    return (
        f"{profile.get('login')} has {total_repos} analyzed public repositories "
        f"with {total_stars} total stars. Strong focus areas: {top_skills}."
    )


def render_public_portfolio(
    username: str,
    profile: dict,
    repositories: list[dict],
    skills: list[dict],
    template_id: str,
) -> str:
    repo_cards = []
    for repo in repositories[:18]:
        description = repo.get("ai_description") or repo.get("description") or describe_repo(repo)
        repo_cards.append(
            f"""
            <article class="card">
              <h3>{repo.get("name")}</h3>
              <p>{description}</p>
              <div class="meta">
                <span>Stars: {int(repo.get("stargazers_count") or 0)}</span>
                <span>Forks: {int(repo.get("forks_count") or 0)}</span>
                <a href="{repo.get("html_url")}" target="_blank" rel="noreferrer">Source</a>
              </div>
            </article>
            """
        )

    skill_tags = " ".join(
        f'<span class="skill">{skill["name"]} ({skill["proficiency"]}/5)</span>' for skill in skills[:24]
    )
    bio = profile.get("bio") or "Software engineer building production-grade systems."
    location = profile.get("location") or "Remote"

    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{username} | DevForge Portfolio</title>
  <style>
    :root {{
      --accent: #0f766e;
      --bg: #f6f8fb;
      --fg: #0f172a;
      --card: #ffffff;
      --muted: #475569;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Sora', system-ui, sans-serif;
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
      background: #e2f2ef;
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
      <span class="badge">DevForge - {template_id}</span>
      <h1>{profile.get("name") or username}</h1>
      <p>@{username} - {location}</p>
      <p>{bio}</p>
      <p>Followers: {int(profile.get("followers") or 0)} | Public Repos: {int(profile.get("public_repos") or 0)}</p>
    </section>
    <section>
      <h2>Core Skills</h2>
      <div class="skills">{skill_tags or "<span class='skill'>No skills extracted yet</span>"}</div>
    </section>
    <section>
      <h2>Projects</h2>
      <div class="grid">{''.join(repo_cards) or "<p>No repositories found.</p>"}</div>
    </section>
  </main>
</body>
</html>
"""
