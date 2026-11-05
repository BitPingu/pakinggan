def test_health_check(client):
    response = client.get("/api/health") # send a get request to health endpoint

    # check results
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

