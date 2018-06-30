# Live variables
VARS = {}

OK_STATUS = 200

# auth
CREDENTIALS_GOOD = {
    "username": "test", "password": "test"
}

CREDENTIALS_BAD = {
    "username": "test", "password": "not_test"
}


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
