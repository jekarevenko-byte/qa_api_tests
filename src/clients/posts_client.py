"""Posts endpoint client."""

from requests import Response
from .base_client import BaseClient


class PostsClient(BaseClient):
    _BASE = "/posts"

    def get_all_posts(self, **params) -> Response:
        return self.get(self._BASE, params=params)

    def get_post(self, post_id: int) -> Response:
        return self.get(f"{self._BASE}/{post_id}")

    def create_post(self, payload: dict) -> Response:
        return self.post(self._BASE, json=payload)

    def update_post(self, post_id: int, payload: dict) -> Response:
        return self.put(f"{self._BASE}/{post_id}", json=payload)

    def patch_post(self, post_id: int, payload: dict) -> Response:
        return self.patch(f"{self._BASE}/{post_id}", json=payload)

    def delete_post(self, post_id: int) -> Response:
        return self.delete(f"{self._BASE}/{post_id}")

    def get_post_comments(self, post_id: int) -> Response:
        return self.get(f"{self._BASE}/{post_id}/comments")
