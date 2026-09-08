def test_developer_can_create_resume(client, dev_token):
    r = client.post("/api/resumes", json={"title": "My CV"},
                    headers={"Authorization": f"Bearer {dev_token}"})
    assert r.status_code == 201


def test_company_cannot_create_resume(client, company_token):
    r = client.post("/api/resumes", json={"title": "Nope"},
                    headers={"Authorization": f"Bearer {company_token}"})
    assert r.status_code == 403
    assert r.get_json()["error"]["code"] == "forbidden"


def test_company_can_create_project(client, company_token):
    r = client.post("/api/projects", json={"title": "Hiring challenge"},
                    headers={"Authorization": f"Bearer {company_token}"})
    assert r.status_code == 201


def test_resume_requires_token(client):
    assert client.post("/api/resumes", json={"title": "x"}).status_code == 401
