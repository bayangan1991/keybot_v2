from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, Any, TypeVar
from collections.abc import Collection

if TYPE_CHECKING:
    from keybot_v2.apps.discord.domain.models import (
        BaseGame,
        BaseTitle,
        BaseMember,
        Platform,
        BaseGuild,
    )

_Game = TypeVar("_Game", bound=BaseGame, covariant=True)
_Title = TypeVar("_Title", bound=BaseTitle)
_Member = TypeVar("_Member", bound=BaseMember)
_Guild = TypeVar("_Guild", bound=BaseGuild)


class BaseSession(Protocol):
    def add(self, instance: Any, _warn: bool = False) -> None:
        ...

    def refresh(self, instance: Any) -> None:
        ...

    def commit(self) -> None:
        ...


class DiscordRepository(Protocol[_Game, _Title, _Member, _Guild]):
    def get_session(self) -> BaseSession:
        ...

    def check_key_exists(self, *, key: str) -> bool:
        ...

    def check_member_has_key(
        self,
        *,
        member: _Member,
        key: str,
    ) -> bool:
        ...

    def get_title(
        self,
        *,
        name: str,
        create: bool = ...,
    ) -> _Title:
        ...

    def get_member(
        self,
        *,
        id: str,
    ) -> _Member:
        ...

    def get_guild(
        self,
        *,
        id: str,
    ) -> _Guild:
        ...

    def add_key(
        self,
        *,
        member: _Member,
        platform: Platform,
        title: _Title,
        key: str,
    ) -> _Game:
        ...

    def remove_key(
        self,
        *,
        member: _Member,
        key: str,
    ) -> tuple[_Title, str]:
        ...

    def get_games(
        self,
        *,
        target: _Member | _Guild,
    ) -> Collection[_Game]:
        ...

    def add_member_to_guild(
        self,
        *,
        member: _Member,
        guild: _Guild,
    ) -> None:
        ...

    def remove_member_from_guild(
        self,
        *,
        member: _Member,
        guild: _Guild,
    ) -> None:
        ...

    def claim_title(
        self,
        *,
        member: _Member,
        title: _Title,
        platform: Platform,
        guild: _Guild,
    ) -> _Game:
        ...
