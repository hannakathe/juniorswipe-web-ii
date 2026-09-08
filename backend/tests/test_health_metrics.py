def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_metrics_exposes_prometheus(client, dev_token):
    client.get("/api/auth/me", headers={"Authorization": f"Bearer {dev_token}"})
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"http_requests_total" in r.data
    assert b"http_request_duration_seconds" in r.data
