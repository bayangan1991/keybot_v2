from __future__ import annotations
from typing import Protocol, Callable
from typing_extensions import Self

from keybot_v2.apps.discord.domain.models import (
    BaseGame,
    BaseTitle,
    BaseMember,
    BaseGuild,
)
from keybot_v2.apps.discord.repositories.types import DiscordRepository, BaseSession

SessionFactory = Callable[..., Callable[..., BaseSession]]


class DiscordUnitOfWork(Protocol):
    repo: DiscordRepository[BaseGame, BaseTitle, BaseMember, BaseGuild]
    session_factory: SessionFactory

    def __init__(self, session_factory: SessionFactory = ...):
        ...

    def __enter__(self) -> Self:
        ...

    def rollback(self) -> None:
        ...

    def commit(self) -> None:
        ...
