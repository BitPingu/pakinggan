# valid track
def test_create_track(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Paranoid Android"
    assert response.json()["duration"] == 383
    assert response.json()["album_id"] == album["id"]
    assert "id" in response.json()


# empty name
def test_create_track_empty_title(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "",
            "duration": 383,
            "album_id": album["id"],
        },
    )

    # rejected by min_length=1
    assert response.status_code == 422


# whitespace name
def test_create_track_whitespace_title(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "   ",
            "duration": 383,
            "album_id": album["id"],
        },
    )

    # rejected by trim
    assert response.status_code == 422


# negative durations
def test_create_track_negative_duration(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": -1,
            "album_id": album["id"],
        },
    )

    # rejected by ge=0
    assert response.status_code == 422


# invalid id
def test_create_track_invalid_album_id(client):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": 0,
        },
    )

    # rejected by gt=0
    assert response.status_code == 422


# nonexistent album
def test_create_track_album_not_found(client):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# optional duration
def test_create_track_without_duration(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "album_id": album["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["duration"] is None


# retrieving all tracks
def test_get_tracks(client, album):
    # create tracks associated with the album
    client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    client.post(
        "/api/tracks/",
        json={
            "title": "Karma Police",
            "duration": 261,
            "album_id": album["id"],
        },
    )

    # verify correct tracks
    response = client.get("/api/tracks/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {track["title"] for track in response.json()} == {
        "Paranoid Android",
        "Karma Police",
    }


# retrieving an individual track
def test_get_track(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # verify correct track
    response = client.get(f"/api/tracks/{track_id}")

    assert response.status_code == 200
    assert response.json()["id"] == track_id
    assert response.json()["title"] == "Paranoid Android"
    assert response.json()["duration"] == 383
    assert response.json()["album_id"] == album["id"]


# track doesn't exist
def test_get_track_not_found(client):
    # verify unknown track
    response = client.get("/api/tracks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Track not found"}


# updating a track
def test_update_track(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # attempt to update the track
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == track_id
    assert response.json()["title"] == "Karma Police"
    assert response.json()["duration"] == 261
    assert response.json()["album_id"] == album["id"]


# updating a track that doesn't exist
def test_update_track_not_found(client, album):
    # attempt to update the track
    response = client.put(
        "/api/tracks/9999",
        json={
            "title": "Karma Police",
            "duration": 261,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Track not found"}


# updating a track with a nonexistent album
def test_update_track_album_not_found(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # attempt to update the track
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "album_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# updating a track with invalid data
def test_update_track_empty_title(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # attempt to update the track
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "",
            "duration": 383,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422


# updating a track with negative duration
def test_update_track_negative_duration(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # attempt to update the track
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": -1,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422


# updating a track to another valid album
def test_update_track_album(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # creates an album associated with the artist
    new_album_response = client.post(
        "/api/albums/",
        json={
            "title": "The Bends",
            "artist_id": album["artist_id"],
        },
    )
    new_album_id = new_album_response.json()["id"]

    # attempt to update the track
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": new_album_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["album_id"] == new_album_id


# deleting a track
def test_delete_track(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # attempt to delete the track
    response = client.delete(f"/api/tracks/{track_id}")

    assert response.status_code == 204

    # verify deletion
    get_response = client.get(f"/api/tracks/{track_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Track not found"}


# deleting a track that doesn't exist
def test_delete_track_not_found(client):
    # attempt to delete the track
    response = client.delete("/api/tracks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Track not found"}
