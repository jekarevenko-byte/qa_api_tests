"""
Base HTTP client wrapping requests.Session.
Handles base URL, default headers, timeout, and logging.
"""

import logging
from typing import Any

import requests
from requests import Response

from configs import config

logger = logging.getLogger(__name__)


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

    # ── public HTTP methods ──────────────────────────────────────────────────

    def get(self, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log("GET", url, **kwargs)
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        self._response_log(response)
        return response

    def post(self, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log("POST", url, **kwargs)
        response = self.session.post(url, timeout=self.timeout, **kwargs)
        self._response_log(response)
        return response

    def put(self, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log("PUT", url, **kwargs)
        response = self.session.put(url, timeout=self.timeout, **kwargs)
        self._response_log(response)
        return response

    def patch(self, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log("PATCH", url, **kwargs)
        response = self.session.patch(url, timeout=self.timeout, **kwargs)
        self._response_log(response)
        return response

    def delete(self, path: str, **kwargs: Any) -> Response:
        url = self._url(path)
        self._log("DELETE", url, **kwargs)
        response = self.session.delete(url, timeout=self.timeout, **kwargs)
        self._response_log(response)
        return response
