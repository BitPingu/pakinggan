from datetime import datetime, timezone

from app.models.listening_history import ListeningHistory
from app.models.track import Track


# Retrieves the authenticated user's listening history.
def test_get_listening_history(client, user, track, db_session, auth_headers):
    # Creates a listening-history entry.
    db_track = db_session.get(Track, track["id"])
    played_at = datetime(2026, 11, 25, 15, 30, tzinfo=timezone.utc)

    history = ListeningHistory(
        user_id=user["id"],
        track_id=db_track.id,
        played_at=played_at,
    )

    db_session.add(history)
    db_session.flush()

    # Retrieves the listening history.
    response = client.get(
        "/api/listening-history/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    entry = response.json()[0]

    assert entry["id"] == history.id
    assert entry["track"]["id"] == track["id"]
    assert entry["track"]["title"] == "Paranoid Android"
    assert entry["track"]["duration"] == 383
    assert entry["track"]["artist"]["name"] == "Radiohead"
    assert entry["track"]["album"]["title"] == "OK Computer"
    assert entry["played_at"] is not None


# Returns an empty list when the user has no listening history.
def test_get_empty_listening_history(client, auth_headers):
    # Retrieves the user's listening history.
    response = client.get(
        "/api/listening-history/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


# Only returns listening-history entries belonging to the authenticated user.
def test_get_only_own_listening_history(client, user, track, db_session, auth_headers):
    # Creates a second user.
    second_user_response = client.post(
        "/api/users/",
        json={
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "securepassword123",
        },
    )

    second_user = second_user_response.json()

    # Creates a listening-history entry for the second user.
    db_track = db_session.get(Track, track["id"])

    history = ListeningHistory(
        user_id=second_user["id"],
        track_id=db_track.id,
        played_at=datetime(2026, 11, 25, 15, 30, tzinfo=timezone.utc),
    )

    db_session.add(history)
    db_session.flush()

    # Retrieves the first user's listening history.
    response = client.get(
        "/api/listening-history/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


# Returns listening-history entries in newest-first order.
def test_get_listening_history_ordered_by_played_at(
    client, user, track, db_session, auth_headers
):
    # Creates listening-history entries with different play timestamps.
    db_track = db_session.get(Track, track["id"])

    older_history = ListeningHistory(
        user_id=user["id"],
        track_id=db_track.id,
        played_at=datetime(2026, 11, 24, 15, 30, tzinfo=timezone.utc),
    )

    newer_history = ListeningHistory(
        user_id=user["id"],
        track_id=db_track.id,
        played_at=datetime(2026, 11, 25, 15, 30, tzinfo=timezone.utc),
    )

    db_session.add_all([older_history, newer_history])
    db_session.flush()

    # Retrieves the user's listening history.
    response = client.get(
        "/api/listening-history/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2
    assert history[0]["id"] == newer_history.id
    assert history[1]["id"] == older_history.id


# Supports pagination of listening-history entries.
def test_get_listening_history_pagination(
    client, user, track, db_session, auth_headers
):
    # Creates three listening-history entries.
    db_track = db_session.get(Track, track["id"])

    history_entries = [
        ListeningHistory(
            user_id=user["id"],
            track_id=db_track.id,
            played_at=datetime(2026, 11, day, 15, 30, tzinfo=timezone.utc),
        )
        for day in (23, 24, 25)
    ]

    db_session.add_all(history_entries)
    db_session.flush()

    # Retrieves the two most recent entries.
    response = client.get(
        "/api/listening-history/?limit=2&offset=0",
        headers=auth_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2
    assert history[0]["played_at"].startswith("2026-11-25")
    assert history[1]["played_at"].startswith("2026-11-24")

    # Skips the two most recent entries.
    response = client.get(
        "/api/listening-history/?limit=2&offset=2",
        headers=auth_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["played_at"].startswith("2026-11-23")


# Rejects invalid listening-history pagination parameters.
def test_get_listening_history_invalid_pagination(client, auth_headers):
    # Rejects a limit below the minimum.
    response = client.get(
        "/api/listening-history/?limit=0",
        headers=auth_headers,
    )

    assert response.status_code == 422

    # Rejects a limit above the maximum.
    response = client.get(
        "/api/listening-history/?limit=101",
        headers=auth_headers,
    )

    assert response.status_code == 422

    # Rejects a negative offset.
    response = client.get(
        "/api/listening-history/?offset=-1",
        headers=auth_headers,
    )

    assert response.status_code == 422


# Rejects requests without an authentication token.
def test_get_listening_history_unauthenticated(client):
    response = client.get("/api/listening-history/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
