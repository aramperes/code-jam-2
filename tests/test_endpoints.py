import pytest
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from tests.fixtures import client

OK_STATUS = 200

# auth
CREDENTIALS_GOOD = {
    "username": "test", "password": "test"
}
CREDENTIALS_BAD = {
    "username": "test", "password": "not_test"
}

# Live variables
VARS = {}


# Utils
def assert_json_status(response, code):
    assert response.is_json
    assert response.status_code == code


def with_auth_headers(headers=None):
    headers = headers or {}
    if "oauth" in VARS:
        access_token = VARS["oauth"]["access_token"]
        headers["Authorization"] = "Bearer {0}".format(access_token)
    return headers


def with_bad_auth_headers(headers=None):
    headers = headers or {}
    headers["Authorization"] = "Bearer not_a_token"
    return headers


def store_check_auth(response):
    VARS["oauth"] = response.json
    assert VARS["oauth"].get("token_type") == "bearer"
    assert "access_token" in VARS["oauth"]
    assert "expires" in VARS["oauth"]
    assert "refresh_token" in VARS["oauth"]


# Tests
def test_index(client: client):
    response = client.get('/')
    assert_json_status(response, OK_STATUS)


def test_not_found(client: client):
    response = client.get('/not_a_route')
    assert_json_status(response, NotFound.code)


@pytest.mark.dependency
def test_register(client: client):
    # register with no credentials
    response = client.post("/auth/register", json={})
    assert_json_status(response, BadRequest.code)

    # register with credentials
    response = client.post("/auth/register", json=CREDENTIALS_GOOD)
    assert_json_status(response, OK_STATUS)


@pytest.mark.dependency(depends=["test_register"])
def test_login(client: client):
    # login with no credentials
    response = client.post("/auth/login", json={})
    assert_json_status(response, BadRequest.code)

    # login with incorrect credentials
    response = client.post("/auth/login", json=CREDENTIALS_BAD)
    assert_json_status(response, Unauthorized.code)

    # successful login
    response = client.post("/auth/login", json=CREDENTIALS_GOOD)
    assert_json_status(response, OK_STATUS)
    store_check_auth(response)


@pytest.mark.dependency(depends=["test_login"])
def test_refresh_token(client: client):
    # refresh token with no token
    response = client.post("/auth/refresh", json={})
    assert_json_status(response, BadRequest.code)

    # refresh token with incorrect token
    response = client.post("/auth/refresh", json={"refresh_token": "not a refresh token"})
    assert_json_status(response, Unauthorized.code)

    # refresh token with correct token
    response = client.post("/auth/refresh", json={"refresh_token": VARS["oauth"]["refresh_token"]})
    assert_json_status(response, OK_STATUS)
    store_check_auth(response)


@pytest.mark.dependency(depends=["test_login"])
def test_use_auth(client: client):
    # access auth'ed resource without auth
    response = client.get("/me")
    assert_json_status(response, Unauthorized.code)

    # access auth'ed resource with incorrect auth
    response = client.get("/me", headers=with_bad_auth_headers())
    assert_json_status(response, Unauthorized.code)

    # access auth'ed resource with correct auth
    response = client.get("/me", headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)
    assert response.json["username"] == CREDENTIALS_GOOD["username"]
