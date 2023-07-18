from ...core.types import BaseSession
from ..unit_of_work.types import GameUnitOfWork
from .expections import KeyAlreadyExists
from .models import Game, Platform, Title


def add_key(
    *,
    owner_id: str,
    title_name: str,
    platform: Platform,
    key: str,
    uow: GameUnitOfWork[BaseSession],
) -> Game:
    if not uow.repo.check_key_exists(key=key, owner_id=owner_id):
        new_game = uow.repo.add_key(
            owner_id=owner_id, platform=platform, title_name=title_name, key=key
        )
        return new_game
    else:
        raise KeyAlreadyExists()


def remove_key(
    *,
    owner_id: str,
    key: str,
    uow: GameUnitOfWork[BaseSession],
) -> tuple[Title, str]:
    popped_key = uow.repo.remove_key(owner_id=owner_id, key=key)
    uow.commit()
    return popped_key
