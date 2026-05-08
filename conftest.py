"""
conftest.py  –  shared fixtures for the entire test suite.
"""

import pytest
from src.clients import UsersClient, PostsClient


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
