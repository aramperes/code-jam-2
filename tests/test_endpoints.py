import pytest
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from tests.fixtures import client
from tests.util import assert_json_status, store_check_auth, with_bad_auth_headers, with_auth_headers, OK_STATUS, \
    CREDENTIALS_GOOD, CREDENTIALS_BAD, VARS


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


@pytest.mark.dependency(depends=["test_login"])
def test_create_story(client: client):
    # create story without auth
    response = client.post("/story")
    assert_json_status(response, Unauthorized.code)

    # create story with defaults
    response = client.post("/story", headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)
    VARS["story_public"] = response.json
    assert "id" in VARS["story_public"]
    assert "sentences" in VARS["story_public"]
    assert "public" in VARS["story_public"]
    assert "media" in VARS["story_public"]
    assert "url" in VARS["story_public"]
    assert VARS["story_public"]["public"] is True

    # create private story
    response = client.post("/story", headers=with_auth_headers(), json={"public": False})
    assert_json_status(response, OK_STATUS)
    VARS["story_private"] = response.json
    assert "id" in VARS["story_private"]
    assert "sentences" in VARS["story_private"]
    assert "public" in VARS["story_private"]
    assert "media" in VARS["story_private"]
    assert "url" in VARS["story_private"]
    assert VARS["story_private"]["public"] is False


@pytest.mark.dependency(depends=["test_create_story"])
def test_list_own_stories(client: client):
    # list own stories without auth
    response = client.get("/stories")
    assert_json_status(response, Unauthorized.code)

    # list own stories with auth
    response = client.get("/stories", headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)
    assert len(response.json) is 2


@pytest.mark.dependency(depends=["test_create_story"])
def test_list_user_stories(client: client):
    # list public stories (without auth)
    response = client.get("/stories/user/{0}".format(CREDENTIALS_GOOD["username"]))
    assert_json_status(response, OK_STATUS)
    for story in response.json:
        assert story["public"] is True

    # list all stories (with auth)
    response = client.get("/stories/user/{0}".format(CREDENTIALS_GOOD["username"]), headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)


@pytest.mark.dependency(depends=["test_create_story"])
def test_get_story_info(client: client):
    # get public story (without auth)
    response = client.get("/story/{0}".format(VARS["story_public"]["id"]))
    assert_json_status(response, OK_STATUS)
    assert response.json["id"] == VARS["story_public"]["id"]
    assert response.json["author"] == CREDENTIALS_GOOD["username"]

    # get private story (without auth)
    response = client.get("/story/{0}".format(VARS["story_private"]["id"]))
    assert_json_status(response, Unauthorized.code)

    # get private story (with auth)
    response = client.get("/story/{0}".format(VARS["story_private"]["id"]), headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)
    assert response.json["id"] == VARS["story_private"]["id"]
    assert response.json["author"] == CREDENTIALS_GOOD["username"]

    # get non-existent story
    response = client.get("/story/{0}".format("not_a_story"))
    assert_json_status(response, NotFound.code)


@pytest.mark.dependency(depends=["test_create_story"])
def test_play_story(client: client):
    # play public story (without auth)
    response = client.get("/story/{0}/play".format(VARS["story_public"]["id"]))
    assert response.status_code == OK_STATUS

    # play private story (without auth)
    response = client.get("/story/{0}/play".format(VARS["story_private"]["id"]))
    assert response.status_code == Unauthorized.code

    # play private story (with auth)
    response = client.get("/story/{0}/play".format(VARS["story_private"]["id"]), headers=with_auth_headers())
    assert response.status_code == OK_STATUS

    # play non-existent story (without auth)
    response = client.get("/story/{0}/play".format("not_a_story"))
    assert response.status_code == NotFound.code


@pytest.mark.dependency(depends=["test_play_story"])
def test_edit_story(client: client):
    # edit story (without auth)
    response = client.put("/story/{0}".format(VARS["story_private"]["id"]), json={"public": True})
    assert_json_status(response, Unauthorized.code)

    # edit story (with auth)
    response = client.put("/story/{0}".format(VARS["story_private"]["id"]), json={"public": True},
                          headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)

    # check if story is now public
    response = client.get("/story/{0}".format(VARS["story_private"]["id"]))
    assert_json_status(response, OK_STATUS)


@pytest.mark.dependency(depends=["test_play_story"])
def test_delete_story(client: client):
    # delete story (without auth)
    response = client.delete("/story/{0}".format(VARS["story_public"]["id"]))
    assert_json_status(response, Unauthorized.code)

    # delete story (with auth)
    response = client.delete("/story/{0}".format(VARS["story_public"]["id"]), headers=with_auth_headers())
    assert_json_status(response, OK_STATUS)

    # check if deleted story is really gone
    response = client.get("/story/{0}".format(VARS["story_public"]["id"]))
    assert_json_status(response, NotFound.code)
