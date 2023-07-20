from typing import Callable, Protocol, TypeVar

from src.apps.core.types import BaseUnitOfWork
from src.apps.discord.repositories.types import BaseSession, DiscordRepository

SessionFactory = Callable[..., Callable[..., BaseSession]]

_S = TypeVar("_S", bound=BaseSession)


class DiscordUnitOfWork(BaseUnitOfWork[_S], Protocol):
    repo: DiscordRepository[_S]
