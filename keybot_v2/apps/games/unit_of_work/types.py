from typing import Protocol, TypeVar

from keybot_v2.apps.core.types import BaseSession, BaseUnitOfWork
from keybot_v2.apps.games.repositories.types import GameRepository

_S = TypeVar("_S", bound=BaseSession)


class GameUnitOfWork(BaseUnitOfWork[_S], Protocol):
    repo: GameRepository[_S]
