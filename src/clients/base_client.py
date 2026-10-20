"""
Base HTTP client wrapping requests.Session.
Handles base URL, default headers, timeout, logging
and Allure reporting (every call is an Allure step with request/response attachments).
"""

import json
import logging
from typing import Any

import allure
import requests
from requests import Response

from configs import config

logger = logging.getLogger(__name__)

# Large bodies (e.g. 100 posts) are cut so the Allure report stays light.
_MAX_ATTACHMENT_CHARS = 50_000


class BaseClient:
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or config.BASE_URL).rstrip("/")
        self.timeout = timeout or config.TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

        if config.API_KEY:
            self.session.headers.update({"Authorization": f"Bearer {config.API_KEY}"})

    # ── private helpers ──────────────────────────────────────────────────────

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _log(self, method: str, url: str, **kwargs: Any) -> None:
        logger.info("%s %s | params=%s body=%s", method.upper(), url, kwargs.get("params"), kwargs.get("json"))

    def _response_log(self, response: Response) -> None:
        logger.info("← %s %s  (%.0f ms)", response.status_code, response.url, response.elapsed.total_seconds() * 1000)

    # ── Allure helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _dump(data: Any) -> str:
        text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        return text[:_MAX_ATTACHMENT_CHARS]

    def _attach_request(self, method: str, url: str, **kwargs: Any) -> None:
        # Never put the Authorization header (API key) into the report.
        headers = {k: v for k, v in self.session.headers.items() if k.lower() != "authorization"}
        details = {
            "method": method.upper(),
            "url": url,
            "params": kwargs.get("params"),
            "headers": headers,
            "body": kwargs.get("json"),
        }
        allure.attach(self._dump(details), name="Request", attachment_type=allure.attachment_type.JSON)

    def _attach_response(self, response: Response) -> None:
        try:
            body: Any = response.json()
        except ValueError:
            body = response.text
        details = {
            "status_code": response.status_code,
            "reason": response.reason,
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000),
            "headers": dict(response.headers),
            "body": body,
        }
        allure.attach(self._dump(details), name="Response", attachment_type=allure.attachment_type.JSON)

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log(method, url, **kwargs)
        with allure.step(f"{method.upper()} {url}"):
            self._attach_request(method, url, **kwargs)
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            self._response_log(response)
            self._attach_response(response)
        return response

    # ── public HTTP methods ──────────────────────────────────────────────────

    def get(self, path: str, **kwargs: Any) -> Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Response:
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Response:
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Response:
        return self._request("DELETE", path, **kwargs)
