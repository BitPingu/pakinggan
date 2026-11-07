# valid artist
# verify that an artist can be successfully created
def test_create_artist(client):
    # send a post request to artists endpoint
    response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    # check results
    assert response.status_code == 201
    assert response.json()["name"] == "Radiohead"
    assert "id" in response.json()


# empty name
# verify that an empty artist name is rejected
def test_create_artist_empty_name(client):
    response = client.post(
        "/api/artists/",
        json={"name": ""},
    )

    # rejected by min_length=1
    assert response.status_code == 422


# whitespace name
# verify that whitespace-only names are rejected
def test_create_artist_whitespace_name(client):
    response = client.post(
        "/api/artists/",
        json={"name": "   "},
    )

    # rejected by trim
    assert response.status_code == 422


# retrieving all artists
def test_get_artists(client, artist):
    # verify correct artists
    response = client.get("/api/artists/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == artist["name"]


# retrieving an existing artist
def test_get_artist(client, artist):
    # verify correct artist
    response = client.get(f"/api/artists/{artist['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == artist["id"]
    assert response.json()["name"] == artist["name"]


# artist doesn't exist
# requests an ID that doesn't exist and verifies the 404 response
def test_get_artist_not_found(client):
    # verify unknown artist
    response = client.get("/api/artists/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# updating an artist
def test_update_artist(client, artist):
    # attempt to update the artist
    response = client.put(
        f"/api/artists/{artist['id']}",
        json={"name": "The Smile"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == artist["id"]
    assert response.json()["name"] == "The Smile"


# updating an artist that doesn't exist
# attempts to update an artist that doesn't exist and expects a 404
def test_update_artist_not_found(client):
    # attempt to update the artist
    response = client.put(
        "/api/artists/9999",
        json={"name": "The Smile"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# deleting an artist
# verify that an artist can be successfully deleted
def test_delete_artist(client, artist):
    # attempt to delete the artist
    response = client.delete(f"/api/artists/{artist['id']}")

    assert response.status_code == 204  # check for no content

    # verify deletion
    get_response = client.get(f"/api/artists/{artist['id']}")

    assert get_response.status_code == 404  # check for not found


# deleting an artist that doesn't exist
# verify that deleting an artist that doesn't exist returns the correct error
def test_delete_artist_not_found(client):
    # attempt to delete the artist
    response = client.delete("/api/artists/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# deleting an artist that has albums
# verify that deleting an artist with associated albums triggers the
# expected database error and rolls back the transaction
def test_delete_artist_with_albums(client, album):
    artist_id = album["artist_id"]

    # attempt to delete the artist
    response = client.delete(f"/api/artists/{artist_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Cannot delete an artist that has associated albums"
    )

    # verify artist still exists
    get_response = client.get(f"/api/artists/{artist_id}")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Radiohead"


# retrieving all albums belonging to an artist
def test_get_artist_albums(client, artist):
    # create albums associated with the artist
    client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist["id"],
        },
    )
    client.post(
        "/api/albums/",
        json={
            "title": "In Rainbows",
            "artist_id": artist["id"],
        },
    )

    # verify correct albums
    response = client.get(f"/api/artists/{artist['id']}/albums")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "OK Computer"
    assert response.json()[1]["title"] == "In Rainbows"


# existing artist with no albums
def test_get_artist_albums_empty(client, artist):
    # verify correct albums
    response = client.get(f"/api/artists/{artist['id']}/albums")

    assert response.status_code == 200
    assert response.json() == []


# album but artist doesn't exist
def test_get_artist_albums_artist_not_found(client):
    response = client.get("/api/artists/9999/albums")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}
