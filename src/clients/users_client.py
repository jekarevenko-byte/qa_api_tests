"""Users endpoint client."""

from requests import Response
from .base_client import BaseClient


class UsersClient(BaseClient):
    _BASE = "/users"

    def get_all_users(self, **params) -> Response:
        return self.get(self._BASE, params=params)

    def get_user(self, user_id: int) -> Response:
        return self.get(f"{self._BASE}/{user_id}")

    def create_user(self, payload: dict) -> Response:
        return self.post(self._BASE, json=payload)

    def update_user(self, user_id: int, payload: dict) -> Response:
        return self.put(f"{self._BASE}/{user_id}", json=payload)

    def patch_user(self, user_id: int, payload: dict) -> Response:
        return self.patch(f"{self._BASE}/{user_id}", json=payload)

    def delete_user(self, user_id: int) -> Response:
        return self.delete(f"{self._BASE}/{user_id}")

    def get_user_posts(self, user_id: int) -> Response:
        return self.get(f"{self._BASE}/{user_id}/posts")
