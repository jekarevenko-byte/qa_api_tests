"""
Tests for /users endpoint.

Covered:
  GET  /users          – list all users
  GET  /users/{id}     – get single user
  POST /users          – create user
  PUT  /users/{id}     – full update
  PATCH /users/{id}    – partial update
  DELETE /users/{id}   – delete user
  GET  /users/{id}/posts – user's posts
  Negative: 404 on unknown user
"""

import pytest
from src.clients import UsersClient
from src.models.schemas import UserModel, PostModel
from src.utils.assertions import (
    assert_ok, assert_created, assert_no_content, assert_not_found,
    assert_json, assert_schema, assert_field_equals,
    assert_field_present, assert_list_not_empty, assert_response_time,
)
from src.utils.factories import make_user


@pytest.mark.users
class TestGetUsers:
    """GET /users"""

    @pytest.mark.smoke
    def test_get_all_users_status_200(self, users_client: UsersClient):
        response = users_client.get_all_users()
        assert_ok(response)

    def test_get_all_users_returns_list(self, users_client: UsersClient):
        response = users_client.get_all_users()
        data = assert_json(response)
        assert_list_not_empty(data, "users")

    def test_get_all_users_response_time(self, users_client: UsersClient):
        response = users_client.get_all_users()
        assert_response_time(response, max_ms=3000)

    def test_get_all_users_schema(self, users_client: UsersClient):
        response = users_client.get_all_users()
        data = assert_json(response)
        users = assert_schema(data, UserModel)
        assert len(users) == 10  # JSONPlaceholder has 10 seed users

    @pytest.mark.smoke
    def test_get_single_user_status_200(self, users_client: UsersClient, existing_user_id):
        response = users_client.get_user(existing_user_id)
        assert_ok(response)

    def test_get_single_user_schema(self, users_client: UsersClient, existing_user_id):
        response = users_client.get_user(existing_user_id)
        data = assert_json(response)
        user = assert_schema(data, UserModel)
        assert user.id == existing_user_id

    def test_get_single_user_fields(self, users_client: UsersClient, existing_user_id):
        response = users_client.get_user(existing_user_id)
        data = assert_json(response)
        assert_field_present(data, "id", "name", "username", "email", "address", "company")

    def test_get_user_posts(self, users_client: UsersClient, existing_user_id):
        response = users_client.get_user_posts(existing_user_id)
        assert_ok(response)
        data = assert_json(response)
        assert_list_not_empty(data, "user posts")
        posts = assert_schema(data, PostModel)
        assert all(p.userId == existing_user_id for p in posts)


@pytest.mark.users
@pytest.mark.negative
class TestGetUserNegative:
    """Negative GET /users scenarios."""

    def test_get_nonexistent_user_returns_404(self, users_client: UsersClient, nonexistent_id):
        response = users_client.get_user(nonexistent_id)
        assert_not_found(response)


@pytest.mark.users
class TestCreateUser:
    """POST /users"""

    @pytest.mark.smoke
    def test_create_user_status_201(self, users_client: UsersClient):
        payload = make_user()
        response = users_client.create_user(payload)
        assert_created(response)

    def test_create_user_returns_id(self, users_client: UsersClient):
        payload = make_user()
        response = users_client.create_user(payload)
        data = assert_json(response)
        assert "id" in data, "Response should contain 'id' for newly created resource"
        assert isinstance(data["id"], int)

    def test_create_user_name_persisted(self, users_client: UsersClient):
        payload = make_user(name="Test User QA")
        response = users_client.create_user(payload)
        data = assert_json(response)
        assert_field_equals(data, "name", "Test User QA")

    def test_create_user_email_persisted(self, users_client: UsersClient):
        payload = make_user(email="qa@example.com")
        response = users_client.create_user(payload)
        data = assert_json(response)
        assert_field_equals(data, "email", "qa@example.com")


@pytest.mark.users
class TestUpdateUser:
    """PUT /users/{id}"""

    def test_full_update_status_200(self, users_client: UsersClient, existing_user_id):
        payload = make_user(name="Updated Name")
        response = users_client.update_user(existing_user_id, payload)
        assert_ok(response)

    def test_full_update_name_reflected(self, users_client: UsersClient, existing_user_id):
        payload = make_user(name="Updated Name")
        response = users_client.update_user(existing_user_id, payload)
        data = assert_json(response)
        assert_field_equals(data, "name", "Updated Name")

    def test_partial_update_status_200(self, users_client: UsersClient, existing_user_id):
        response = users_client.patch_user(existing_user_id, {"name": "Patched"})
        assert_ok(response)

    def test_partial_update_name_reflected(self, users_client: UsersClient, existing_user_id):
        response = users_client.patch_user(existing_user_id, {"name": "Patched"})
        data = assert_json(response)
        assert_field_equals(data, "name", "Patched")


@pytest.mark.users
class TestDeleteUser:
    """DELETE /users/{id}"""

    def test_delete_user(self, users_client: UsersClient, existing_user_id):
        response = users_client.delete_user(existing_user_id)
        assert_no_content(response)
