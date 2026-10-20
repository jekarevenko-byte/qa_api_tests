"""
conftest.py  –  shared fixtures for the entire test suite.
"""

import allure
import pytest
from configs import config
from src.clients import UsersClient, PostsClient


# ── Allure ────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _allure_readable_title(request):
    """Show 'Get all users status 200' instead of 'test_get_all_users_status_200' in the report."""
    name = request.node.name  # may end with a parametrize id, e.g. "[5]"
    base, bracket, params = name.partition("[")
    title = base.removeprefix("test_").replace("_", " ").strip().capitalize()
    allure.dynamic.title(f"{title}{bracket}{params}")


def pytest_sessionstart(session):
    """Write environment.properties so the report has an 'Environment' widget."""
    alluredir = getattr(session.config.option, "allure_report_dir", None)
    if not alluredir:
        return
    import os
    import platform
    import pathlib

    out = pathlib.Path(str(alluredir))
    out.mkdir(parents=True, exist_ok=True)
    (out / "environment.properties").write_text(
        "\n".join(
            [
                f"BASE_URL={config.BASE_URL}",
                f"TIMEOUT={config.TIMEOUT}",
                f"Python={platform.python_version()}",
                f"OS={platform.platform()}",
                f"Commit={os.getenv('GITHUB_SHA', 'local')[:7]}",
                f"Branch={os.getenv('GITHUB_REF_NAME', 'local')}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


# ── Client fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def users_client() -> UsersClient:
    return UsersClient()


@pytest.fixture(scope="session")
def posts_client() -> PostsClient:
    return PostsClient()


# ── Seed data fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def existing_user_id() -> int:
    """A known user ID that exists in the API."""
    return 1


@pytest.fixture(scope="session")
def existing_post_id() -> int:
    """A known post ID that exists in the API."""
    return 1


@pytest.fixture(scope="session")
def nonexistent_id() -> int:
    return 99999
