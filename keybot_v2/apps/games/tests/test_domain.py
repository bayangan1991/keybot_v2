from typing import Callable

import pytest

from keybot_v2.apps.games.domain.services import (
    add_key,
    remove_key,
)
from keybot_v2.apps.games.repositories.fake.repo import FakeSession
from keybot_v2.apps.games.unit_of_work.fake import FakeUnitOfWork

GAME_NAME = "Game Name"


@pytest.fixture
def session_factory() -> Callable[[], FakeSession]:
    return lambda: FakeSession()


def test_can_add_key(session_factory: Callable[[], FakeSession]) -> None:
    with FakeUnitOfWork(session_factory=session_factory) as uow:
        member_id = "1"

        add_key(
            owner_id=member_id,
            title_name=GAME_NAME,
            platform="steam",
            key="123",
            uow=uow,
        )

    assert len(uow.repo.games) == 1
    assert uow.repo.games.pop().title.name == GAME_NAME


def test_can_remove_key(session_factory: Callable[..., FakeSession]) -> None:
    with FakeUnitOfWork(session_factory=session_factory) as uow:
        member_id = "1"
        test_key = "123"
        uow.repo.add_key(
            owner_id=member_id,
            platform="steam",
            title_name=GAME_NAME,
            key=test_key,
        )

        uow.commit()

        popped_title, key = remove_key(owner_id=member_id, key=test_key, uow=uow)

        title = uow.repo.get_title(name=GAME_NAME, create=False)
        assert popped_title == title
        assert test_key == key
        assert len(uow.repo.games) == 0
        assert not uow.repo.check_key_exists(key=test_key, owner_id=member_id)
