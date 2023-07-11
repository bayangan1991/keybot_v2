from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, Any
from collections.abc import Collection

if TYPE_CHECKING:
    from keybot_v2.domain.models import (
        BaseGame,
        BaseTitle,
        BaseMember,
        Platform,
        BaseGuild,
    )


class BaseSession(Protocol):
    def add(self, instance: Any, _warn: bool = False) -> None:
        ...

    def refresh(self, instance: Any) -> None:
        ...

    def commit(self) -> None:
        ...


class BaseRepository(Protocol):
    def get_session(self) -> BaseSession:
        ...

    def check_key_exists(
        self,
        *,
        session: BaseSession,
        key: str,
    ) -> bool:
        ...

    def check_member_has_key(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        key: str,
    ) -> bool:
        ...

    def get_title(
        self,
        *,
        session: BaseSession,
        name: str,
        create: bool = ...,
    ) -> BaseTitle:
        ...

    def get_member(
        self,
        *,
        session: BaseSession,
        id: str,
    ) -> BaseMember:
        ...

    def get_guild(
        self,
        *,
        session: BaseSession,
        id: str,
    ) -> BaseGuild:
        ...

    def add_key(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        platform: Platform,
        title: BaseTitle,
        key: str,
    ) -> BaseGame:
        ...

    def remove_key(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        key: str,
    ) -> tuple[BaseTitle, str]:
        ...

    def get_games(
        self,
        *,
        session: BaseSession,
        target: BaseMember | BaseGuild,
    ) -> Collection[BaseGame]:
        ...

    def add_member_to_guild(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        guild: BaseGuild,
    ) -> None:
        ...

    def remove_member_from_guild(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        guild: BaseGuild,
    ) -> None:
        ...

    def claim_title(
        self,
        *,
        session: BaseSession,
        member: BaseMember,
        title: BaseTitle,
        platform: Platform,
        guild: BaseGuild,
    ) -> BaseGame:
        ...
