from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING, Protocol, TypeVar

from src.apps.core.types import BaseRepository, BaseSession

if TYPE_CHECKING:
    from src.apps.discord.domain.models import Guild, Member

_S_co = TypeVar("_S_co", bound=BaseSession, covariant=True)


class DiscordRepository(BaseRepository[_S_co], Protocol):
    def get_session(self) -> BaseSession:
        ...

    def get_member(
        self,
        *,
        id: str,
    ) -> Member:
        ...

    def get_guild(
        self,
        *,
        id: str,
    ) -> Guild:
        ...

    def add_member_to_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        ...

    def remove_member_from_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        ...

    def get_guild_members(self, guild_id: str) -> Collection[Member]:
        ...
