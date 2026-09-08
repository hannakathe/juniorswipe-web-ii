def _h(t):
    return {"Authorization": f"Bearer {t}"}


def _project(client, token, title="Proj"):
    return client.post("/api/projects", json={"title": title},
                       headers=_h(token)).get_json()["id"]


def test_create_and_list_task(client, dev_token):
    pid = _project(client, dev_token)
    r = client.post("/api/tasks",
                    json={"title": "Do thing", "project_id": pid, "status": "todo"},
                    headers=_h(dev_token))
    assert r.status_code == 201
    assert r.get_json()["project_id"] == pid

    r = client.get(f"/api/tasks?project_id={pid}", headers=_h(dev_token))
    assert r.status_code == 200
    assert any(t["title"] == "Do thing" for t in r.get_json()["items"])


def test_create_task_invalid_status(client, dev_token):
    pid = _project(client, dev_token)
    r = client.post("/api/tasks",
                    json={"title": "x", "project_id": pid, "status": "bogus"},
                    headers=_h(dev_token))
    assert r.status_code == 422


def test_cannot_add_task_to_foreign_project(client, dev_token, company_token):
    pid = _project(client, dev_token, "Owned by dev")
    r = client.post("/api/tasks", json={"title": "sneak", "project_id": pid},
                    headers=_h(company_token))
    assert r.status_code == 404


def test_task_list_requires_auth(client):
    assert client.get("/api/tasks").status_code == 401


def test_nested_project_tasks_route(client, dev_token):
    pid = _project(client, dev_token)
    client.post(f"/api/projects/{pid}/tasks", json={"title": "nested"},
                headers=_h(dev_token))
    r = client.get(f"/api/projects/{pid}/tasks", headers=_h(dev_token))
    assert r.get_json()["total"] == 1
