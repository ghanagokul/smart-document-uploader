from tests.conftest import client, create_test_user, TestingSessionLocal


def test_signup_success():
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "newuser@example.com", "password": "password123", "full_name": "New User"},
    )
    assert response.status_code == 201


def test_signup_duplicate_email_fails():
    with TestingSessionLocal() as db:
        create_test_user(db, email="existing@example.com")
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "existing@example.com", "password": "anotherpassword", "full_name": "Someone Else"},
    )
    assert response.status_code == 409


def test_signup_invalid_email_format_returns_422():
    response = client.post("/api/v1/auth/signup", json={"email": "not-an-email", "password": "password123"})
    assert response.status_code == 422


def test_signup_missing_password_returns_422():
    response = client.post("/api/v1/auth/signup", json={"email": "newuser@example.com"})
    assert response.status_code == 422


def test_login_success_after_signup():
    client.post(
        "/api/v1/auth/signup",
        json={"email": "flowuser@example.com", "password": "correcthorse", "full_name": "Flow User"},
    )
    response = client.post("/api/v1/auth/login", json={"email": "flowuser@example.com", "password": "correcthorse"})
    assert response.status_code == 200


def test_login_wrong_password():
    with TestingSessionLocal() as db:
        create_test_user(db, email="ghanagokul@example.com", password="correctpassword")
    response = client.post("/api/v1/auth/login", json={"email": "ghanagokul@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_login_nonexistent_email():
    response = client.post("/api/v1/auth/login", json={"email": "doesnotexist@example.com", "password": "whatever123"})
    assert response.status_code == 401


def test_login_invalid_email_format_returns_422():
    response = client.post("/api/v1/auth/login", json={"email": "not-an-email-at-all", "password": "password123"})
    assert response.status_code == 422


def test_login_missing_password_field_returns_422():
    response = client.post("/api/v1/auth/login", json={"email": "ghanagokul@example.com"})
    assert response.status_code == 422


def test_login_missing_email_field_returns_422():
    response = client.post("/api/v1/auth/login", json={"password": "password123"})
    assert response.status_code == 422


def test_login_empty_body_returns_422():
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422


def test_login_wrong_content_type_returns_422():
    response = client.post("/api/v1/auth/login", data={"email": "ghanagokul@example.com", "password": "password123"})
    assert response.status_code == 422