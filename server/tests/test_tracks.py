# valid track
def test_create_track(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Paranoid Android"
    assert response.json()["duration"] == 383
    assert response.json()["artist_id"] == album["artist_id"]
    assert response.json()["album_id"] == album["id"]
    assert "id" in response.json()


# empty name
def test_create_track_empty_title(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    # Rejected by min_length=1.
    assert response.status_code == 422


# whitespace name
def test_create_track_whitespace_title(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "   ",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    # Rejected by trimming.
    assert response.status_code == 422


# negative durations
def test_create_track_negative_duration(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": -1,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    # Rejected by ge=0.
    assert response.status_code == 422


# invalid ID
def test_create_track_invalid_album_id(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": 0,
        },
    )

    # Rejected by gt=0.
    assert response.status_code == 422


# nonexistent album
def test_create_track_album_not_found(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# nonexistent artist
def test_create_track_artist_not_found(client):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# album belongs to a different artist
def test_create_track_album_artist_mismatch(client, album):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Thom Yorke"},
    )
    different_artist_id = artist_response.json()["id"]

    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": different_artist_id,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Album does not belong to the specified artist"
    }


# optional duration
def test_create_track_without_duration(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["duration"] is None


# creates a track without an album
def test_create_track_without_album(client, album):
    response = client.post(
        "/api/tracks/",
        json={
            "title": "Street Spirit (Fade Out)",
            "duration": 251,
            "artist_id": album["artist_id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Street Spirit (Fade Out)"
    assert response.json()["duration"] == 251
    assert response.json()["artist_id"] == album["artist_id"]
    assert response.json()["album_id"] is None


# retrieving all tracks
def test_get_tracks(client, album):
    # Create tracks associated with the album.
    client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    client.post(
        "/api/tracks/",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    # Verify correct tracks.
    response = client.get("/api/tracks/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {track["title"] for track in response.json()} == {
        "Paranoid Android",
        "Karma Police",
    }


# returns an empty list when no tracks exist
def test_get_tracks_empty(client):
    response = client.get("/api/tracks/")

    assert response.status_code == 200
    assert response.json() == []


# retrieving an individual track
def test_get_track(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Verify correct track.
    response = client.get(f"/api/tracks/{track_id}")

    assert response.status_code == 200
    assert response.json()["id"] == track_id
    assert response.json()["title"] == "Paranoid Android"
    assert response.json()["duration"] == 383
    assert response.json()["artist_id"] == album["artist_id"]
    assert response.json()["album_id"] == album["id"]


# track doesn't exist
def test_get_track_not_found(client):
    # Verify unknown track.
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
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Attempt to update the track.
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == track_id
    assert response.json()["title"] == "Karma Police"
    assert response.json()["duration"] == 261
    assert response.json()["artist_id"] == album["artist_id"]
    assert response.json()["album_id"] == album["id"]


# updating a track that doesn't exist
def test_update_track_not_found(client, album):
    # Attempt to update the track.
    response = client.put(
        "/api/tracks/9999",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": album["artist_id"],
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
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Attempt to update the track.
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": album["artist_id"],
            "album_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# updating a track with a nonexistent artist
def test_update_track_artist_not_found(client, track, album):
    response = client.put(
        f"/api/tracks/{track['id']}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": 9999,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# updating a track with an album belonging to a different artist
def test_update_track_album_artist_mismatch(client, track, album):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Thom Yorke"},
    )
    different_artist_id = artist_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track['id']}",
        json={
            "title": "Karma Police",
            "duration": 261,
            "artist_id": different_artist_id,
            "album_id": album["id"],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Album does not belong to the specified artist"
    }


# updating a track with invalid data
def test_update_track_empty_title(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Attempt to update the track.
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422


# updating a track with a whitespace-only title
def test_update_track_whitespace_title(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "   ",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422


# updating a track with an invalid album ID
def test_update_track_invalid_album_id(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": 0,
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
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Attempt to update the track.
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": -1,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422


# updating a track without a duration
def test_update_track_without_duration(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 200
    assert response.json()["duration"] is None


# verifies that an invalid update leaves the track unchanged
def test_update_track_invalid_data_unchanged(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )

    assert response.status_code == 422

    get_response = client.get(f"/api/tracks/{track_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Paranoid Android"
    assert get_response.json()["duration"] == 383


# updating a track to another valid album
def test_update_track_album(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Creates an album associated with the same artist.
    new_album_response = client.post(
        "/api/albums/",
        json={
            "title": "The Bends",
            "artist_id": album["artist_id"],
        },
    )
    new_album_id = new_album_response.json()["id"]

    # Attempt to update the track.
    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": new_album_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["album_id"] == new_album_id


# removes the album association from a track
def test_update_track_without_album(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    response = client.put(
        f"/api/tracks/{track_id}",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": None,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == track_id
    assert response.json()["album_id"] is None


# deleting a track
def test_delete_track(client, album):
    create_response = client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "artist_id": album["artist_id"],
            "album_id": album["id"],
        },
    )
    track_id = create_response.json()["id"]

    # Attempt to delete the track.
    response = client.delete(f"/api/tracks/{track_id}")

    assert response.status_code == 204

    # Verify deletion.
    get_response = client.get(f"/api/tracks/{track_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Track not found"}


# deleting a track that doesn't exist
def test_delete_track_not_found(client):
    # Attempt to delete the track.
    response = client.delete("/api/tracks/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Track not found"}
