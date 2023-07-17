from __future__ import annotations

from types import TracebackType

from typing_extensions import Self

from keybot_v2.apps.core.types import SessionFactory
from keybot_v2.apps.games.unit_of_work.types import GameUnitOfWork

from keybot_v2.apps.games.repositories.fake.repo import FakeSession, FakeRepository


class FakeUnitOfWork(GameUnitOfWork[FakeSession]):
    repo: FakeRepository

    def __init__(self, session_factory: SessionFactory[FakeSession]) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self.repo = FakeRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def rollback(self) -> None:
        return None

    def commit(self) -> None:
        self.session.commited = True
