from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar


class BaseSession(Protocol):
    def add(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        ...

    def refresh(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        ...

    def commit(self) -> None:
        ...


_S = TypeVar("_S", bound=BaseSession)
SessionFactory = Callable[..., _S]


class BaseRepository(Protocol[_S]):
    def __init__(
        self,
        session: _S = ...,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        ...
