"""
Integration test: end-to-end user ↔ posts flow.
Verifies that cross-resource relationships are consistent.
"""

import pytest
from src.clients import UsersClient, PostsClient
from src.utils.assertions import assert_ok, assert_json, assert_list_not_empty


@pytest.mark.regression
class TestUserPostsIntegration:
    """Cross-resource consistency checks."""

    def test_all_user_ids_in_posts_are_valid(
        self,
        users_client: UsersClient,
        posts_client: PostsClient,
    ):
        users_resp = users_client.get_all_users()
        assert_ok(users_resp)
        valid_user_ids = {u["id"] for u in assert_json(users_resp)}

        posts_resp = posts_client.get_all_posts()
        assert_ok(posts_resp)
        posts = assert_json(posts_resp)

        invalid = [p for p in posts if p["userId"] not in valid_user_ids]
        assert not invalid, (
            f"Found {len(invalid)} posts with non-existent userId: "
            f"{[p['id'] for p in invalid[:5]]}"
        )

    def test_user_posts_match_global_posts(
        self,
        users_client: UsersClient,
        posts_client: PostsClient,
        existing_user_id: int,
    ):
        # via /users/{id}/posts
        via_user = users_client.get_user_posts(existing_user_id)
        assert_ok(via_user)
        user_posts = assert_json(via_user)

        # via /posts?userId={id}
        via_filter = posts_client.get_all_posts(userId=existing_user_id)
        assert_ok(via_filter)
        filtered_posts = assert_json(via_filter)

        ids_via_user = sorted(p["id"] for p in user_posts)
        ids_via_filter = sorted(p["id"] for p in filtered_posts)

        assert ids_via_user == ids_via_filter, (
            "Post lists from /users/{id}/posts and /posts?userId={id} don't match"
        )

    def test_each_user_has_at_least_one_post(
        self,
        users_client: UsersClient,
        posts_client: PostsClient,
    ):
        users_resp = users_client.get_all_users()
        users = assert_json(users_resp)

        for user in users:
            response = users_client.get_user_posts(user["id"])
            assert_ok(response)
            posts = assert_json(response)
            assert_list_not_empty(posts, f"posts for user {user['id']}")
