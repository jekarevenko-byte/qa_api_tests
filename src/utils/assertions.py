"""
Custom assertion helpers.
Provide meaningful failure messages and reduce boilerplate in tests.
Every helper is an Allure step, so checks are visible in the report.
"""

from typing import Any

import allure
from requests import Response
from pydantic import BaseModel


# ── HTTP ─────────────────────────────────────────────────────────────────────

def assert_status(response: Response, expected: int) -> None:
    with allure.step(f"Check status code is {expected}"):
        assert response.status_code == expected, (
            f"Expected HTTP {expected}, got {response.status_code}\n"
            f"URL: {response.url}\n"
            f"Body: {response.text[:500]}"
        )


def assert_ok(response: Response) -> None:
    assert_status(response, 200)


def assert_created(response: Response) -> None:
    assert_status(response, 201)


def assert_no_content(response: Response) -> None:
    with allure.step("Check status code is 200 or 204"):
        assert response.status_code in (200, 204), (
            f"Expected 200 or 204, got {response.status_code}"
        )


def assert_not_found(response: Response) -> None:
    assert_status(response, 404)


def assert_bad_request(response: Response) -> None:
    assert_status(response, 400)


# ── JSON / Schema ─────────────────────────────────────────────────────────────

def assert_json(response: Response) -> dict:
    with allure.step("Check Content-Type is JSON and parse body"):
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, (
            f"Expected JSON content-type, got: {content_type}"
        )
        return response.json()


def assert_schema(data: dict | list, model: type[BaseModel]) -> BaseModel | list[BaseModel]:
    """Validate response data against a Pydantic model."""
    with allure.step(f"Validate JSON schema ({model.__name__})"):
        if isinstance(data, list):
            return [model.model_validate(item) for item in data]
        return model.model_validate(data)


# ── Field-level ───────────────────────────────────────────────────────────────

def assert_field_equals(data: dict, field: str, expected: Any) -> None:
    with allure.step(f"Check field '{field}' equals {expected!r}"):
        assert field in data, f"Field '{field}' not found in response: {list(data.keys())}"
        assert data[field] == expected, (
            f"Field '{field}': expected {expected!r}, got {data[field]!r}"
        )


def assert_field_present(data: dict, *fields: str) -> None:
    with allure.step(f"Check fields are present: {', '.join(fields)}"):
        missing = [f for f in fields if f not in data]
        assert not missing, f"Missing fields in response: {missing}"


def assert_list_not_empty(data: list, label: str = "list") -> None:
    with allure.step(f"Check {label} is a non-empty list"):
        assert isinstance(data, list), f"Expected list, got {type(data).__name__}"
        assert len(data) > 0, f"Expected non-empty {label}"


def assert_response_time(response: Response, max_ms: int = 2000) -> None:
    with allure.step(f"Check response time <= {max_ms} ms"):
        elapsed_ms = response.elapsed.total_seconds() * 1000
        assert elapsed_ms <= max_ms, (
            f"Response too slow: {elapsed_ms:.0f} ms (max {max_ms} ms)"
        )
