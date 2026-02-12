from __future__ import annotations

from pathlib import Path


class DeployerService:
    def __init__(self, output_dir: str = "generated_portfolios"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def deploy_static_portfolio(self, subdomain: str, html: str) -> str:
        target = self.output_dir / subdomain
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.html").write_text(html, encoding="utf-8")
        return f"/generated/{subdomain}/index.html"
