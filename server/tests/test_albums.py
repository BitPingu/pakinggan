# valid album
def test_create_album(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "OK Computer"
    assert response.json()["artist_id"] == artist_id
    assert "id" in response.json()


# empty name
def test_create_album_empty_title(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    response = client.post(
        "/api/albums/",
        json={
            "title": "",
            "artist_id": artist_id,
        },
    )

    # rejected by min_length=1
    assert response.status_code == 422


# whitespace name
def test_create_album_whitespace_title(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    response = client.post(
        "/api/albums/",
        json={
            "title": "   ",
            "artist_id": artist_id,
        },
    )

    # rejected by trim
    assert response.status_code == 422


# invalid id
def test_create_album_invalid_artist_id(client):
    response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": 0,
        },
    )

    # rejected by gt=0
    assert response.status_code == 422


# nonexistent artist
def test_create_album_artist_not_found(client):
    response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# retrieving all albums
def test_get_albums(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # create albums associated with the artist
    client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )
    client.post(
        "/api/albums/",
        json={
            "title": "In Rainbows",
            "artist_id": artist_id,
        },
    )

    # verify correct albums
    response = client.get("/api/albums/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "OK Computer"
    assert response.json()[1]["title"] == "In Rainbows"


# retrieving a single album
def test_get_album(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    create_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = create_response.json()["id"]

    # verify correct album
    response = client.get(f"/api/albums/{album_id}")

    assert response.status_code == 200
    assert response.json()["id"] == album_id
    assert response.json()["title"] == "OK Computer"
    assert response.json()["artist_id"] == artist_id


# album doesn't exist
def test_get_album_not_found(client):
    # verify unknown album
    response = client.get("/api/albums/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# updating an album
def test_update_album(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    create_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = create_response.json()["id"]

    # attempt to update the album
    response = client.put(
        f"/api/albums/{album_id}",
        json={
            "title": "OK Computer (Remastered)",
            "artist_id": artist_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == album_id
    assert response.json()["title"] == "OK Computer (Remastered)"
    assert response.json()["artist_id"] == artist_id


# updating an album that doesn't exist
def test_update_album_not_found(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # attempt to update the album
    response = client.put(
        "/api/albums/9999",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# updating an album with a nonexistent artist
def test_update_album_artist_not_found(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    create_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = create_response.json()["id"]

    # attempt to update the album
    response = client.put(
        f"/api/albums/{album_id}",
        json={
            "title": "OK Computer (Remastered)",
            "artist_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# deleting an album
def test_delete_album(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    create_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = create_response.json()["id"]

    # attempt to delete the album
    response = client.delete(f"/api/albums/{album_id}")

    assert response.status_code == 204 # check for no content

    # verify deletion
    get_response = client.get(f"/api/albums/{album_id}")

    assert get_response.status_code == 404 # check for not found


# deleting an album that doesn't exist
def test_delete_album_not_found(client):
    # attempt to delete the album
    response = client.delete("/api/albums/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}


# deleting an album that has tracks
def test_delete_album_with_tracks(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    album_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = album_response.json()["id"]

    # creates a track associated with the album
    client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album_id,
        },
    )

    # attempt to delete the album
    response = client.delete(f"/api/albums/{album_id}")

    assert response.status_code == 500
    assert response.json() == {"detail": "A database error occurred"}

    # verify album still exists
    get_response = client.get(f"/api/albums/{album_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "OK Computer"


# retrieving tracks belonging to an album
def test_get_album_tracks(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    album_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = album_response.json()["id"]

    # create tracks associated with the album
    client.post(
        "/api/tracks/",
        json={
            "title": "Paranoid Android",
            "duration": 383,
            "album_id": album_id,
        },
    )
    client.post(
        "/api/tracks/",
        json={
            "title": "Karma Police",
            "duration": 261,
            "album_id": album_id,
        },
    )

    # verify correct tracks
    response = client.get(f"/api/albums/{album_id}/tracks")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Paranoid Android"
    assert response.json()[1]["title"] == "Karma Police"


# existing album with no tracks
def test_get_album_tracks_empty(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    album_response = client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    album_id = album_response.json()["id"]

    # verify correct tracks
    response = client.get(f"/api/albums/{album_id}/tracks")

    assert response.status_code == 200
    assert response.json() == []


# album doesn't exist
def test_get_album_tracks_album_not_found(client):
    response = client.get("/api/albums/9999/tracks")

    assert response.status_code == 404
    assert response.json() == {"detail": "Album not found"}

