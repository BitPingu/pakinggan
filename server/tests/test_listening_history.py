from datetime import datetime, timezone

from app.models.listening_history import ListeningHistory


# Creates and retrieves a listening-history entry.
def test_create_listening_history(db_session, user, track):
    played_at = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)

    history = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=played_at,
    )

    db_session.add(history)
    db_session.flush()

    result = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .first()
    )

    assert result is not None
    assert result.track_id == track["id"]
    assert result.played_at == played_at
    assert result.created_at is not None


# Verifies the relationships between users, tracks, and listening history.
def test_listening_history_relationships(db_session, user, track):
    history = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=datetime.now(timezone.utc),
    )

    db_session.add(history)
    db_session.flush()

    assert history.user.id == user["id"]
    assert history.track.id == track["id"]
    assert history in history.user.listening_history
    assert history in history.track.listening_history


# Deletes a user's listening history when the user is deleted.
def test_delete_user_cascades_listening_history(db_session, user, track):
    history = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=datetime.now(timezone.utc),
    )

    db_session.add(history)
    db_session.flush()

    db_session.delete(history.user)
    db_session.flush()

    result = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.user_id == user["id"])
        .first()
    )

    assert result is None


# Deletes listening-history entries when their track is deleted.
def test_delete_track_cascades_listening_history(db_session, user, track):
    history = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=datetime.now(timezone.utc),
    )

    db_session.add(history)
    db_session.flush()

    db_session.delete(history.track)
    db_session.flush()

    result = (
        db_session.query(ListeningHistory)
        .filter(ListeningHistory.track_id == track["id"])
        .first()
    )

    assert result is None


# Allows multiple listening-history entries for the same track.
def test_multiple_plays_of_same_track(db_session, user, track):
    first_play = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc),
    )

    second_play = ListeningHistory(
        user_id=user["id"],
        track_id=track["id"],
        played_at=datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc),
    )

    db_session.add_all([first_play, second_play])
    db_session.flush()

    results = (
        db_session.query(ListeningHistory)
        .filter(
            ListeningHistory.user_id == user["id"],
            ListeningHistory.track_id == track["id"],
        )
        .all()
    )

    assert len(results) == 2
    assert {entry.played_at for entry in results} == {
        first_play.played_at,
        second_play.played_at,
    }
