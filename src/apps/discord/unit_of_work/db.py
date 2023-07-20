from __future__ import annotations

from types import TracebackType

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from src.apps.discord.repositories.db.repo import SQLModelRepository
from src.apps.discord.unit_of_work.types import DiscordUnitOfWork
from src.config import settings

ENGINE = create_engine(settings.db.url, echo=settings.db.echo)
DEFAULT_SESSION_FACTORY = sessionmaker(bind=ENGINE, class_=Session)


class DBUnitOfWork(DiscordUnitOfWork[Session]):
    repo: SQLModelRepository

    def __init__(
        self, session_factory: sessionmaker[Session] = DEFAULT_SESSION_FACTORY
    ):
        super().__init__(session_factory=session_factory)
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.repo = SQLModelRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
