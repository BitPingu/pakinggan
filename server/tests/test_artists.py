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


# retrieve all artists
# creates two artists and verifies that both are returned
def test_get_artists(client):
    client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )
    client.post(
        "/api/artists/",
        json={"name": "Pink Floyd"},
    )

    # verify correct artists
    response = client.get("/api/artists/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Radiohead"
    assert response.json()[1]["name"] == "Pink Floyd"


# retrieve existing artist
# creates an artist, retrieves its generated ID, and requests that specific artist
def test_get_artist(client):
    create_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = create_response.json()["id"]

    # verify correct artist
    response = client.get(f"/api/artists/{artist_id}")

    assert response.status_code == 200
    assert response.json()["id"] == artist_id
    assert response.json()["name"] == "Radiohead"


# artist doesn't exist
# requests an ID that doesn't exist and verifies the 404 response
def test_get_artist_not_found(client):
    # verify unknown artist
    response = client.get("/api/artists/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# update existing artist
# creates an artist, updates its name, and verifies the returned artist
def test_update_artist(client):
    create_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = create_response.json()["id"]

    # attempt to update the artist
    response = client.put(
        f"/api/artists/{artist_id}",
        json={"name": "The Smile"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == artist_id
    assert response.json()["name"] == "The Smile"


# artist doesn't exist
# attempts to update an artist that doesn't exist and expects a 404
def test_update_artist_not_found(client):
    # attempt to update the artist
    response = client.put(
        "/api/artists/9999",
        json={"name": "The Smile"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# delete existing artist
# verify that an artist can be successfully deleted
def test_delete_artist(client):
    create_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = create_response.json()["id"]

    # attempt to delete the artist
    response = client.delete(f"/api/artists/{artist_id}")

    assert response.status_code == 204 # check for no content

    # verify deletion
    get_response = client.get(f"/api/artists/{artist_id}")

    assert get_response.status_code == 404 # check for not found


# artist doesn't exist
# verify that deleting an artist that doesn't exist returns the correct error
def test_delete_artist_not_found(client):
    # attempt to delete the artist
    response = client.delete("/api/artists/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


# artist has albums
# verify that deleting an artist with associated albums triggers the 
# expected database error and rolls back the transaction
def test_delete_artist_with_albums(client):
    artist_response = client.post(
        "/api/artists/",
        json={"name": "Radiohead"},
    )

    artist_id = artist_response.json()["id"]

    # creates an album associated with the artist
    client.post(
        "/api/albums/",
        json={
            "title": "OK Computer",
            "artist_id": artist_id,
        },
    )

    # attempt to delete the artist
    response = client.delete(f"/api/artists/{artist_id}")

    print("Delete status:", response.status_code)
    print("Delete response:", response.text)

    assert response.status_code == 500
    assert response.json() == {"detail": "A database error occurred"}

    # verify artist still exists
    get_response = client.get(f"/api/artists/{artist_id}")

    print("Get status:", get_response.status_code)
    print("Get response:", get_response.text)

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Radiohead"

