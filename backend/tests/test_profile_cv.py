import io


def _h(t):
    return {"Authorization": f"Bearer {t}"}


def test_get_and_update_profile(client, dev_token):
    r = client.get("/api/profiles/me", headers=_h(dev_token))
    assert r.status_code == 200

    r = client.put("/api/profiles/me",
                   json={"headline": "Backend dev", "skills": ["python", "sql"]},
                   headers=_h(dev_token))
    assert r.status_code == 200
    body = r.get_json()
    assert body["headline"] == "Backend dev"
    assert body["skills"] == ["python", "sql"]


def test_profile_requires_auth(client):
    assert client.get("/api/profiles/me").status_code == 401


def test_create_list_and_authorize_resume(client, dev_token, company_token):
    r = client.post("/api/resumes", json={"title": "CV 2026", "summary": "junior dev"},
                    headers=_h(dev_token))
    assert r.status_code == 201
    rid = r.get_json()["id"]
    assert r.get_json()["is_primary"] is True

    r = client.get("/api/resumes", headers=_h(dev_token))
    assert r.get_json()["total"] == 1

    # Another user must not see or fetch it.
    assert client.get(f"/api/resumes/{rid}", headers=_h(company_token)).status_code == 404


def test_resume_file_upload_and_download(client, dev_token):
    data = {
        "title": "CV with file",
        "file": (io.BytesIO(b"%PDF-1.4 fake pdf"), "cv.pdf"),
    }
    r = client.post("/api/resumes", data=data, content_type="multipart/form-data",
                    headers=_h(dev_token))
    assert r.status_code == 201
    body = r.get_json()
    assert body["has_file"] is True
    assert body["size_bytes"] > 0

    r = client.get(f"/api/resumes/{body['id']}/file", headers=_h(dev_token))
    assert r.status_code == 200
    assert r.data == b"%PDF-1.4 fake pdf"
