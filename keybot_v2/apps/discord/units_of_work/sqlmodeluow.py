from __future__ import annotations

from typing import TypeVar, Generic

from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session

from keybot_v2.apps.discord.repositories.db.repo import SQLModelRepository
from keybot_v2.apps.discord.units_of_work.types import DiscordUnitOfWork
from keybot_v2.config import settings


ENGINE = create_engine(settings.db.url, echo=settings.db.echo)
DEFAULT_SESSION_FACTORY = sessionmaker(bind=ENGINE, class_=Session)

_S = TypeVar("_S")


class SQLModelUnitOfWork(DiscordUnitOfWork, Generic[_S]):
    repo: SQLModelRepository
    session_factory: sessionmaker[_S]

    def __init__(self, session_factory: sessionmaker[_S] = DEFAULT_SESSION_FACTORY):
        super().__init__(session_factory=session_factory)
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.repo = SQLModelRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
