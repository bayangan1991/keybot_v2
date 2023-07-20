from types import TracebackType

from typing_extensions import Self

from keybot_v2.apps.core.types import SessionFactory
from keybot_v2.apps.discord.repositories.fake.repo import FakeRepository, FakeSession
from keybot_v2.apps.discord.unit_of_work.types import DiscordUnitOfWork


class FakeUnitOfWork(DiscordUnitOfWork[FakeSession]):
    repo: FakeRepository

    def __init__(self, session_factory: SessionFactory[FakeSession]) -> None:
        self.committed = False
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
        self.session.committed = True
