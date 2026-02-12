import pytest

from app.services.github import parse_github_username


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://github.com/octocat", "octocat"),
        ("github.com/octocat/", "octocat"),
        ("@octocat", "octocat"),
        ("octocat", "octocat"),
    ],
)
def test_parse_github_username_valid(raw: str, expected: str):
    assert parse_github_username(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "https://example.com/notgithub",
        "https://github.com/",
    ],
)
def test_parse_github_username_invalid(raw: str):
    with pytest.raises(ValueError):
        parse_github_username(raw)
