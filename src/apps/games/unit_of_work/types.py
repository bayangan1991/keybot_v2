from typing import Protocol, TypeVar

from src.apps.core.types import BaseSession, BaseUnitOfWork
from src.apps.games.repositories.types import GameRepository

_S = TypeVar("_S", bound=BaseSession)


class GameUnitOfWork(BaseUnitOfWork[_S], Protocol):
    repo: GameRepository[_S]
