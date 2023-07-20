from __future__ import annotations

from types import TracebackType
from typing import Any, Callable, Protocol, TypeVar

from typing_extensions import Self


class BaseSession(Protocol):
    def add(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        ...

    def refresh(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        ...

    def commit(self) -> None:
        ...


_S_co = TypeVar("_S_co", bound=BaseSession, covariant=True)


class BaseRepository(Protocol[_S_co]):
    def __init__(
        self,
        session: _S_co,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        ...


_S = TypeVar("_S", bound=BaseSession)
SessionFactory = Callable[..., _S]


class BaseUnitOfWork(Protocol[_S]):
    repo: BaseRepository[_S]
    session_factory: SessionFactory[_S]

    def __init__(
        self,
        session_factory: SessionFactory[_S],
        *args: Any,
        **kwargs: Any,
    ) -> None:
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
