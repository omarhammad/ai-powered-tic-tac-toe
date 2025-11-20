from domain.GameSession import GameSession
from infrastructure.repositories.SessionRepository import SessionRepository


def test_save_session():
    repo = SessionRepository()
    fake_session = GameSession("abc", "PX", "PO")

    repo.save("abc", fake_session)

    assert repo._sessions["abc"] is fake_session


def test_find_existing_session():
    repo = SessionRepository()
    fake_session = GameSession("abc", "PX", "PO")
    repo.save("abc", fake_session)

    found = repo.find("abc")
    assert found is fake_session


def test_find_non_existing_session():
    repo = SessionRepository()
    assert repo.find("xyz") is None
