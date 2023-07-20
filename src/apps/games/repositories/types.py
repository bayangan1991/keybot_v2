from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

from src.apps.core.types import BaseRepository, BaseSession

if TYPE_CHECKING:
    from src.apps.games.domain.models import (
        Game,
        Platform,
        Title,
    )

_S = TypeVar("_S", bound=BaseSession, covariant=True)


class GameRepository(BaseRepository[_S], Protocol):
    def check_key_exists(self, *, key: str, owner_id: str) -> bool:
        ...

    def get_title(
        self,
        *,
        name: str,
        create: bool = ...,
    ) -> Title:
        ...

    def add_key(
        self,
        *,
        owner_id: str,
        platform: Platform,
        title_name: str,
        key: str,
    ) -> Game:
        ...

    def remove_key(
        self,
        *,
        owner_id: str,
        key: str,
    ) -> tuple[Title, str]:
        ...
