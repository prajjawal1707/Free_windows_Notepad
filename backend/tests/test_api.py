import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app

H = {"X-API-Token": settings.token}


@pytest.fixture()
def client(tmp_path):
    settings.data_dir = tmp_path
    with TestClient(create_app()) as c:
        yield c


def auth(token):
    return {**H, "Authorization": f"Bearer {token}"}


def test_health_open(client):
    assert client.get("/health").json()["status"] == "running"


def test_api_token_required(client):
    assert client.get("/api/v1/auth/status").status_code == 401
    assert client.get("/api/v1/auth/status", headers=H).json() == {"has_users": False}


def test_full_flow(client):
    r = client.post("/api/v1/auth/register", headers=H, json={"username": "admin", "password": "secret1", "full_name": "Boss"})
    assert r.status_code == 200 and r.json()["user"]["role"] == "admin"
    token = r.json()["token"]
    assert client.post("/api/v1/auth/register", headers=H, json={"username": "x1x", "password": "secret1"}).status_code == 403
    assert client.get("/api/v1/auth/me", headers=auth(token)).json()["username"] == "admin"
    assert client.get("/api/v1/auth/me", headers=H).status_code == 401

    r = client.post("/api/v1/users/", headers=auth(token), json={"username": "rahul", "password": "secret1"})
    assert r.status_code == 201
    assert client.post("/api/v1/users/", headers=auth(token), json={"username": "RAHUL", "password": "secret1"}).status_code == 409
    assert len(client.get("/api/v1/users/", headers=auth(token)).json()) == 2

    t2 = client.post("/api/v1/auth/login", headers=H, json={"username": "rahul", "password": "secret1"}).json()["token"]
    assert client.post("/api/v1/users/", headers=auth(t2), json={"username": "evil", "password": "secret1"}).status_code == 403

    stats = client.get("/api/v1/dashboard/", headers=auth(token)).json()
    assert stats["total_users"] == 2 and stats["admins"] == 1

    assert client.put("/api/v1/settings/", headers=auth(token), json={"values": {"theme": "dark"}}).json()["theme"] == "dark"
    assert client.delete("/api/v1/users/1", headers=auth(token)).status_code == 400
    assert client.delete("/api/v1/users/2", headers=auth(token)).status_code == 200

    client.post("/api/v1/auth/logout", headers=auth(token))
    assert client.get("/api/v1/auth/me", headers=auth(token)).status_code == 401


def test_bad_login(client):
    client.post("/api/v1/auth/register", headers=H, json={"username": "admin", "password": "secret1"})
    assert client.post("/api/v1/auth/login", headers=H, json={"username": "admin", "password": "nope"}).status_code == 401


def _setup_two(client):
    t1 = client.post("/api/v1/auth/register", headers=H, json={"username": "admin", "password": "secret1"}).json()["token"]
    client.post("/api/v1/users/", headers=auth(t1), json={"username": "rahul", "password": "secret1"})
    t2 = client.post("/api/v1/auth/login", headers=H, json={"username": "rahul", "password": "secret1"}).json()["token"]
    return t1, t2


def test_notes_crud_search_privacy(client):
    t1, t2 = _setup_two(client)
    r = client.post("/api/v1/notes/", headers=auth(t1), json={"title": "Groceries", "content": "milk, eggs", "tags": "home", "pinned": True})
    assert r.status_code == 201
    nid = r.json()["id"]
    client.post("/api/v1/notes/", headers=auth(t1), json={"title": "Work", "content": "call Amit"})
    assert len(client.get("/api/v1/notes/", headers=auth(t1)).json()) == 2
    assert client.get("/api/v1/notes/", headers=auth(t1)).json()[0]["title"] == "Groceries"  # pinned first
    assert len(client.get("/api/v1/notes/?q=amit", headers=auth(t1)).json()) == 1
    # privacy: other user cannot see / edit / delete
    assert client.get("/api/v1/notes/", headers=auth(t2)).json() == []
    assert client.get(f"/api/v1/notes/{nid}", headers=auth(t2)).status_code == 404
    assert client.put(f"/api/v1/notes/{nid}", headers=auth(t2), json={"title": "x"}).status_code == 404
    assert client.delete(f"/api/v1/notes/{nid}", headers=auth(t2)).status_code == 404
    # edit + delete own
    r = client.put(f"/api/v1/notes/{nid}", headers=auth(t1), json={"title": "Groceries v2", "content": "milk", "pinned": False})
    assert r.json()["title"] == "Groceries v2"
    assert client.delete(f"/api/v1/notes/{nid}", headers=auth(t1)).status_code == 200
    assert len(client.get("/api/v1/notes/", headers=auth(t1)).json()) == 1


def test_csv_export_import_roundtrip(client, tmp_path):
    settings.export_dir = tmp_path
    t1, _ = _setup_two(client)
    assert client.get("/api/v1/notes/export", headers=auth(t1)).status_code == 400
    client.post("/api/v1/notes/", headers=auth(t1), json={"title": "A, \"quoted\"", "content": "line1\nline2 नमस्ते", "tags": "x,y"})
    client.post("/api/v1/notes/", headers=auth(t1), json={"title": "=SUM(1)", "content": "-"})
    r = client.get("/api/v1/notes/export", headers=auth(t1)).json()
    assert r["count"] == 2
    text = open(r["path"], encoding="utf-8-sig").read()
    assert "'=SUM(1)" in text  # formula-injection guard
    assert client.post("/api/v1/notes/import", headers=auth(t1), json={"csv": text}).json()["imported"] == 2
    titles = [n["title"] for n in client.get("/api/v1/notes/", headers=auth(t1)).json()]
    assert titles.count("=SUM(1)") == 2 and titles.count('A, "quoted"') == 2
    assert client.post("/api/v1/notes/import", headers=auth(t1), json={"csv": "foo,bar\n1,2"}).status_code == 400
    settings.export_dir = None


def test_user_edit_and_passwords(client):
    t1, t2 = _setup_two(client)
    assert client.put("/api/v1/users/2", headers=auth(t1), json={"full_name": "Rahul K", "role": "admin"}).json()["role"] == "admin"
    assert client.put("/api/v1/users/2", headers=auth(t1), json={"role": "user"}).json()["role"] == "user"
    assert client.put("/api/v1/users/1", headers=auth(t1), json={"role": "user"}).status_code == 400  # last admin
    assert client.put("/api/v1/users/2", headers=auth(t2), json={"role": "admin"}).status_code == 403
    # change own password
    bad = client.post("/api/v1/auth/change-password", headers=auth(t2), json={"current_password": "wrong1", "new_password": "newpass1"})
    assert bad.status_code == 400
    assert client.post("/api/v1/auth/change-password", headers=auth(t2), json={"current_password": "secret1", "new_password": "newpass1"}).status_code == 200
    assert client.post("/api/v1/auth/login", headers=H, json={"username": "rahul", "password": "secret1"}).status_code == 401
    assert client.post("/api/v1/auth/login", headers=H, json={"username": "rahul", "password": "newpass1"}).status_code == 200
    # admin reset
    assert client.put("/api/v1/users/2/password", headers=auth(t1), json={"new_password": "reset123"}).status_code == 200
    assert client.get("/api/v1/auth/me", headers=auth(t2)).status_code == 401  # sessions revoked
    assert client.post("/api/v1/auth/login", headers=H, json={"username": "rahul", "password": "reset123"}).status_code == 200
