from __future__ import annotations

from types import TracebackType
from typing import Protocol, TypeVar

from typing_extensions import Self

from keybot_v2.apps.core.types import BaseSession, SessionFactory
from keybot_v2.apps.games.repositories.types import GameRepository

_S = TypeVar("_S", bound=BaseSession)


class GameUnitOfWork(Protocol[_S]):
    repo: GameRepository[_S]
    session_factory: SessionFactory[_S]

    def __init__(self, session_factory: SessionFactory[_S]) -> None:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...

    def rollback(self) -> None:
        ...

    def commit(self) -> None:
        ...
