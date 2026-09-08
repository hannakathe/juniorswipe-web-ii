def _h(t):
    return {"Authorization": f"Bearer {t}"}


def test_create_project(client, dev_token):
    r = client.post("/api/projects",
                    json={"title": "New API", "description": "d", "status": "open"},
                    headers=_h(dev_token))
    assert r.status_code == 201
    body = r.get_json()
    assert body["title"] == "New API"
    assert body["status"] == "open"
    assert body["owner_id"]


def test_create_project_requires_title(client, dev_token):
    r = client.post("/api/projects", json={"description": "no title"},
                    headers=_h(dev_token))
    assert r.status_code == 422


def test_list_projects_only_own(client, dev_token, company_token):
    client.post("/api/projects", json={"title": "Dev project"}, headers=_h(dev_token))
    client.post("/api/projects", json={"title": "Company project"},
                headers=_h(company_token))
    r = client.get("/api/projects", headers=_h(company_token))
    titles = [p["title"] for p in r.get_json()["items"]]
    assert "Company project" in titles
    assert "Dev project" not in titles


def test_cannot_read_other_users_project_by_id(client, dev_token, company_token):
    pid = client.post("/api/projects", json={"title": "Secret"},
                      headers=_h(dev_token)).get_json()["id"]
    r = client.get(f"/api/projects/{pid}", headers=_h(company_token))
    assert r.status_code == 404


def test_list_projects_pagination(client, dev_token):
    for i in range(5):
        client.post("/api/projects", json={"title": f"P{i}"}, headers=_h(dev_token))
    r = client.get("/api/projects?page=1&per_page=2", headers=_h(dev_token))
    body = r.get_json()
    assert len(body["items"]) == 2
    assert body["total"] >= 5
