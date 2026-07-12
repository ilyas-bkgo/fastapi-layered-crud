import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from main import app
from database import get_db, SCHEMA

# Use a completely separate database file so we don't wipe local dev data
TEST_DB_PATH = "test_app.db"

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    # Setup: Spin up a fresh test database file and run the schema queries to create tables
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    for statement in SCHEMA:
        cursor.execute(statement)
    conn.commit()
    conn.close()

    yield  # The fixture pauses here and lets the test suite execute

    # Teardown: Wipe the test database file once all tests finish to keep the workspace clean
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(name="client")
def client_fixture():
    # Define a temporary database session generator for the duration of the tests
    def override_get_db():
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # Trapdoor: Swap out the production database dependency for our test database connection
    app.dependency_overrides[get_db] = override_get_db

    # Provide the TestClient to hit endpoints inside memory without running a real server
    with TestClient(app) as client:
        yield client

    # Clear the overrides after the test completes so production routes aren't affected
    app.dependency_overrides.clear()


def test_register_user_success(client):
    # Try to register a new user with valid credentials
    response = client.post(
        "/users/",
        json={"username": "tester", "email": "tester@example.com", "password": "supersecretpassword"}
    )
    # Check if the API successfully creates the resource
    assert response.status_code == 201

    # Verify the response matches our user schema and includes generated values
    data = response.json()
    assert data["username"] == "tester"
    assert data["email"] == "tester@example.com"
    assert "id" in data
    assert "created_at" in data


def test_register_user_duplicate_username(client):
    # Attempt to sign up with an identical username to trigger a UNIQUE constraint error
    response = client.post(
        "/users/",
        json={"username": "tester", "email": "different@example.com", "password": "anotherpassword"}
    )
    # The global exception handler should catch the database collision and return a clean 400 Bad Request
    assert response.status_code == 400
    assert response.json() == {"detail": "Username or email already exists"}


def test_create_todo_unauthenticated(client):
    # Try creating a todo without passing an Authorization header to verify the route is guarded
    response = client.post(
        "/todos/",
        json={"name": "Ghost Task", "completed": False}
    )
    # The authentication dependency must block this request with a 401 status code
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_todo_success(client):
    # Step 1: Log in using the registered user credentials to retrieve an authentication token
    login_response = client.post(
        "/users/login",
        data={"username": "tester", "password": "supersecretpassword"}
    )
    assert login_response.status_code == 200

    # Step 2: Extract the signed JWT token string from the login response body
    token_data = login_response.json()
    access_token = token_data["access_token"]

    # Step 3: Format the security token into the standard HTTP Bearer header structure
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 4: Submit a request to create a new todo task alongside the authorization header
    todo_response = client.post(
        "/todos/",
        json={"name": "Build automated tests", "completed": False},
        headers=headers
    )

    # Step 5: Confirm the todo task was successfully committed to the database under this user
    assert todo_response.status_code == 201
    todo_data = todo_response.json()
    assert todo_data["name"] == "Build automated tests"
    assert todo_data["completed"] is False
    assert "id" in todo_data
    assert "created_at" in todo_data
