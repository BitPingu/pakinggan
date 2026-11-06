# verify app is running and responding to requests
def test_health_check(client):
    # send a get request to health endpoint
    response = client.get("/api/health")

    # check results
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

