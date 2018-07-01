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

CREDENTIALS_ALT = {
    "username": "foo", "password": "bar"
}


def other_user(credentials=None, username=None):
    if credentials:
        return CREDENTIALS_ALT if credentials["username"] == CREDENTIALS_GOOD["username"] else CREDENTIALS_GOOD
    elif username:
        return other_user(credentials=from_username(username))


def from_username(username):
    return CREDENTIALS_GOOD if username == CREDENTIALS_GOOD["username"] else CREDENTIALS_ALT


def assert_json_status(response, code):
    assert response.is_json
    assert response.status_code == code


def with_auth_headers(headers=None, credentials=None):
    if credentials is None:
        credentials = CREDENTIALS_GOOD
    headers = headers or {}
    if credentials["username"] in VARS and "oauth" in VARS[credentials["username"]]:
        access_token = VARS[credentials["username"]]["oauth"]["access_token"]
        headers["Authorization"] = "Bearer {0}".format(access_token)
    return headers


def with_bad_auth_headers(headers=None):
    headers = headers or {}
    headers["Authorization"] = "Bearer not_a_token"
    return headers


def store_check_auth(response, credentials=None):
    if credentials is None:
        credentials = CREDENTIALS_GOOD
    VARS[credentials["username"]] = {"oauth": response.json}
    assert VARS[credentials["username"]]["oauth"].get("token_type") == "bearer"
    assert "access_token" in VARS[credentials["username"]]["oauth"]
    assert "expires" in VARS[credentials["username"]]["oauth"]
    assert "refresh_token" in VARS[credentials["username"]]["oauth"]


def refresh_token(credentials=None):
    if credentials is None:
        credentials = CREDENTIALS_GOOD
    return VARS[credentials["username"]]["oauth"]["refresh_token"]
