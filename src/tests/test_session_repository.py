from src.main.python.domain.GameSession import GameSession
from src.main.python.infrastructure.repositories.SessionRepository import SessionRepository


def test_save_session():
    # Test that saving a session stores it in the repository
    repo = SessionRepository()
    fake_session = GameSession("abc", "PX", "PO")

    repo.save("abc", fake_session)

    assert repo._sessions["abc"] is fake_session


def test_find_existing_session():
    # Verify that find() returns the correct stored session
    repo = SessionRepository()
    fake_session = GameSession("abc", "PX", "PO")
    repo.save("abc", fake_session)

    found = repo.find("abc")
    assert found is fake_session


def test_find_non_existing_session():
    # Ensure find() returns None when session does not exist
    repo = SessionRepository()
    assert repo.find("xyz") is None
