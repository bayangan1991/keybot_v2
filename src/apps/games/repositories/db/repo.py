from typing import Any

from sqlmodel import Session, select

from ...domain.expections import TitleDoesNotExist
from ...domain.models import Platform
from ..types import GameRepository
from .models import GameInDB, TitleInDB


class SQLModelRepository(GameRepository[Session]):
    def __init__(self, session: Session, *args: Any, **kwargs: Any):
        self.session = session

    def get_title(
        self,
        *,
        name: str,
        create: bool = True,
    ) -> TitleInDB:
        statement = select(TitleInDB).where(TitleInDB.name == name)

        if title := self.session.exec(statement).first():
            return title

        if create:
            new_title = TitleInDB(name=name)
            return new_title

        raise TitleDoesNotExist()

    def add_key(
        self,
        *,
        owner_id: str,
        platform: Platform,
        title_name: str,
        key: str,
    ) -> GameInDB:
        title = self.get_title(name=title_name)
        new_game = GameInDB(
            owner_id=owner_id,
            platform=platform,
            title_pk=title.pk,
            key=key,
        )
        self.session.add(new_game)
        return new_game

    def remove_key(
        self,
        *,
        owner_id: str,
        key: str,
    ) -> tuple[TitleInDB, str]:
        statement = select(GameInDB).where(
            GameInDB.key == key, GameInDB.owner_id == owner_id
        )
        removed_game = self.session.exec(statement).one()

        self.session.delete(removed_game)

        return removed_game.title, removed_game.key
