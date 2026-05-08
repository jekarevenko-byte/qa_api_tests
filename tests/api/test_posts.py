"""
Tests for /posts endpoint.

Covered:
  GET  /posts          – list all posts
  GET  /posts/{id}     – get single post
  POST /posts          – create post
  PUT  /posts/{id}     – full update
  PATCH /posts/{id}    – partial update
  DELETE /posts/{id}   – delete post
  GET  /posts/{id}/comments – post comments
  Parametrised: multiple valid post IDs
  Negative: 404 on unknown post
"""

import pytest
from src.clients import PostsClient
from src.models.schemas import PostModel, CommentModel
from src.utils.assertions import (
    assert_ok, assert_created, assert_no_content, assert_not_found,
    assert_json, assert_schema, assert_field_equals,
    assert_field_present, assert_list_not_empty, assert_response_time,
)
from src.utils.factories import make_post


@pytest.mark.posts
class TestGetPosts:
    """GET /posts"""

    @pytest.mark.smoke
    def test_get_all_posts_status_200(self, posts_client: PostsClient):
        response = posts_client.get_all_posts()
        assert_ok(response)

    def test_get_all_posts_returns_list(self, posts_client: PostsClient):
        response = posts_client.get_all_posts()
        data = assert_json(response)
        assert_list_not_empty(data, "posts")

    def test_get_all_posts_schema(self, posts_client: PostsClient):
        response = posts_client.get_all_posts()
        data = assert_json(response)
        posts = assert_schema(data, PostModel)
        assert len(posts) == 100  # JSONPlaceholder has 100 seed posts

    def test_get_all_posts_response_time(self, posts_client: PostsClient):
        response = posts_client.get_all_posts()
        assert_response_time(response, max_ms=3000)

    @pytest.mark.smoke
    def test_get_single_post_status_200(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.get_post(existing_post_id)
        assert_ok(response)

    def test_get_single_post_schema(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.get_post(existing_post_id)
        data = assert_json(response)
        post = assert_schema(data, PostModel)
        assert post.id == existing_post_id

    @pytest.mark.parametrize("post_id", [1, 5, 10, 50, 100])
    def test_get_various_post_ids(self, posts_client: PostsClient, post_id: int):
        response = posts_client.get_post(post_id)
        assert_ok(response)
        data = assert_json(response)
        assert_field_equals(data, "id", post_id)

    def test_get_post_comments(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.get_post_comments(existing_post_id)
        assert_ok(response)
        data = assert_json(response)
        assert_list_not_empty(data, "post comments")
        comments = assert_schema(data, CommentModel)
        assert all(c.postId == existing_post_id for c in comments)

    def test_filter_posts_by_user(self, posts_client: PostsClient):
        response = posts_client.get_all_posts(userId=1)
        assert_ok(response)
        data = assert_json(response)
        assert_list_not_empty(data, "filtered posts")
        assert all(p["userId"] == 1 for p in data)


@pytest.mark.posts
@pytest.mark.negative
class TestGetPostNegative:
    """Negative GET /posts scenarios."""

    def test_get_nonexistent_post_returns_404(self, posts_client: PostsClient, nonexistent_id):
        response = posts_client.get_post(nonexistent_id)
        assert_not_found(response)


@pytest.mark.posts
class TestCreatePost:
    """POST /posts"""

    @pytest.mark.smoke
    def test_create_post_status_201(self, posts_client: PostsClient):
        payload = make_post(user_id=1)
        response = posts_client.create_post(payload)
        assert_created(response)

    def test_create_post_id_assigned(self, posts_client: PostsClient):
        payload = make_post(user_id=1)
        response = posts_client.create_post(payload)
        data = assert_json(response)
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_post_fields_persisted(self, posts_client: PostsClient):
        payload = make_post(user_id=3, title="My QA Title", body="Some body text")
        response = posts_client.create_post(payload)
        data = assert_json(response)
        assert_field_equals(data, "title", "My QA Title")
        assert_field_equals(data, "body", "Some body text")
        assert_field_equals(data, "userId", 3)


@pytest.mark.posts
class TestUpdatePost:
    """PUT / PATCH /posts/{id}"""

    def test_full_update_status_200(self, posts_client: PostsClient, existing_post_id):
        payload = make_post(user_id=1, title="Updated")
        response = posts_client.update_post(existing_post_id, payload)
        assert_ok(response)

    def test_full_update_title_reflected(self, posts_client: PostsClient, existing_post_id):
        payload = make_post(user_id=1, title="Updated Title")
        response = posts_client.update_post(existing_post_id, payload)
        data = assert_json(response)
        assert_field_equals(data, "title", "Updated Title")

    def test_partial_update_status_200(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.patch_post(existing_post_id, {"title": "Patched Title"})
        assert_ok(response)

    def test_partial_update_title_reflected(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.patch_post(existing_post_id, {"title": "Patched Title"})
        data = assert_json(response)
        assert_field_equals(data, "title", "Patched Title")


@pytest.mark.posts
class TestDeletePost:
    """DELETE /posts/{id}"""

    def test_delete_post(self, posts_client: PostsClient, existing_post_id):
        response = posts_client.delete_post(existing_post_id)
        assert_no_content(response)
