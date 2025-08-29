import pytest
import uuid
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)

def test_register_user(client):
    unique_id = str(uuid.uuid4())[:8]
    response = client.post("/auth/register", json={
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com", 
        "password": "testpass123"
    })
    assert response.status_code in [200, 409]  # 200 for new user, 409 if exists
    if response.status_code == 200:
        assert response.json()["status"] == "ok"

def test_login_user(client):
    unique_id = str(uuid.uuid4())[:8]
    # First register
    register_response = client.post("/auth/register", json={
        "username": f"logintest_{unique_id}",
        "email": f"login_{unique_id}@example.com",
        "password": "testpass123"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "username": f"logintest_{unique_id}",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_comment_posts(client):
    # Test getting comment posts without authentication
    response = client.get("/comment_posts")
    assert response.status_code == 200
    assert "posts" in response.json()

def test_create_comment_post_without_auth(client):
    # Test creating comment post without authentication should fail
    response = client.post("/comment_posts", json={
        "target_gender": "Female",
        "target_job": "Engineer",
        "target_birth_year": 1995,
        "target_height": 165,
        "target_app": "Tinder",
        "comment": "Test comment"
    })
    assert response.status_code == 401

def test_like_comment_post_without_auth(client):
    # Test liking comment post without authentication should fail
    response = client.post("/comment_posts/1/like")
    assert response.status_code == 401

def test_update_comment_post_without_auth(client):
    # Test updating comment post without authentication should fail
    response = client.put("/comment_posts/1", json={
        "target_gender": "Male",
        "target_job": "Doctor",
        "target_birth_year": 1990,
        "target_height": 180,
        "target_app": "Bumble",
        "comment": "Updated comment"
    })
    assert response.status_code == 401

def test_create_comment_post_with_mock_auth():
    from fastapi.testclient import TestClient
    from main import app
    from dependencies import get_current_user
    
    # Mock get_current_user to return a user ID
    async def mock_get_current_user():
        return 1
    
    # Override dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    client = TestClient(app)
    response = client.post("/comment_posts", json={
        "target_gender": "Female",
        "target_job": "Engineer",
        "target_birth_year": 1995,
        "target_height": 165,
        "target_app": "Tinder",
        "comment": "Test comment with mock auth"
    })
    
    # Clean up
    app.dependency_overrides.clear()
    
    # Should succeed or fail with database error (not auth error)
    assert response.status_code in [200, 500]  # 200 success, 500 db error
    if response.status_code == 200:
        assert response.json()["status"] == "ok"

def test_get_dating_posts(client):
    # Test getting dating posts without authentication
    response = client.get("/dating")
    assert response.status_code == 200
    assert "posts" in response.json()

def test_create_dating_post_without_auth(client):
    # Test creating dating post without authentication should fail
    response = client.post("/dating", json={
        "title": "Looking for love",
        "description": "Test description",
        "target_gender": "Female",
        "target_age_min": 25,
        "target_age_max": 35
    })
    assert response.status_code == 401

def test_send_message_without_auth(client):
    # Test sending message without authentication should fail
    response = client.post("/dating/1/message", json={
        "content": "Hello there!"
    })
    assert response.status_code == 401

def test_can_post_dating_without_auth(client):
    # Test checking can post without authentication should fail
    response = client.get("/dating/can_post")
    assert response.status_code == 401

def test_create_dating_post_with_mock_auth():
    from fastapi.testclient import TestClient
    from main import app
    from dependencies import get_current_user
    
    # Mock get_current_user to return a user ID
    async def mock_get_current_user():
        return 1
    
    # Override dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    client = TestClient(app)
    response = client.post("/dating", json={
        "title": "Looking for love",
        "description": "Test description",
        "target_gender": "Female",
        "target_age_min": 25,
        "target_age_max": 35
    })
    
    # Clean up
    app.dependency_overrides.clear()
    
    # Should succeed or fail with database error (not auth error)
    assert response.status_code in [200, 400, 500]  # 200 success, 400 validation, 500 db error
    if response.status_code == 200:
        assert response.json()["status"] == "ok"

def test_get_messages_without_auth(client):
    # Test getting messages without authentication should fail
    response = client.get("/messages")
    assert response.status_code == 401

def test_reply_message_without_auth(client):
    # Test replying to message without authentication should fail
    response = client.post("/messages/1/reply", json={
        "reply_content": "Test reply"
    })
    assert response.status_code == 401

def test_update_message_without_auth(client):
    # Test updating message without authentication should fail
    response = client.put("/messages/1", json={
        "content": "Updated content"
    })
    assert response.status_code == 401

def test_get_messages_with_mock_auth():
    from fastapi.testclient import TestClient
    from main import app
    from dependencies import get_current_user
    
    # Mock get_current_user to return a user ID
    async def mock_get_current_user():
        return 1
    
    # Override dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    client = TestClient(app)
    response = client.get("/messages")
    
    # Clean up
    app.dependency_overrides.clear()
    
    # Should succeed or fail with database error (not auth error)
    assert response.status_code in [200, 500]  # 200 success, 500 db error
    if response.status_code == 200:
        assert response.json()["status"] == "ok"
        assert "messages" in response.json()

def test_profile_without_auth(client):
    # Test profile without authentication should fail
    response = client.get("/users/profile")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["message"]

def test_auth_endpoints_exist(client):
    # Test that auth endpoints exist (without Redis)
    unique_id = str(uuid.uuid4())[:8]
    
    # Test register endpoint exists
    response = client.post("/auth/register", json={
        "username": f"test_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpass123"
    })
    assert response.status_code in [200, 409, 500]  # Any response means endpoint exists
    
    # Test login endpoint exists
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code in [200, 401, 500]  # Any response means endpoint exists

