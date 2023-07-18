from typing import Any

from pydantic import BaseModel

from keybot_v2.apps.core.types import BaseSession
from keybot_v2.apps.discord.domain.models import Platform
from keybot_v2.apps.games.domain.expections import (
    KeyAlreadyExists,
    KeyDoesNotExist,
    TitleDoesNotExist,
)
from keybot_v2.apps.games.domain.models import Game, Title
from keybot_v2.apps.games.repositories.types import GameRepository


class FakeSession(BaseSession):
    def __init__(self) -> None:
        self.committed: bool = False
        self.items: set[BaseModel] = set()

    def commit(self) -> None:
        self.committed = True

    def add(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        self.items.add(instance)

    def refresh(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        ...


class FakeRepository(GameRepository[FakeSession]):
    titles: set[Title]
    games: set[Game]

    def __init__(
        self,
        session: FakeSession,
        *,
        titles: set[Title] | None = None,
        games: set[Game] | None = None,
    ) -> None:
        self.session = session

        self.titles = set()
        self.games = set()

    def init_objects(
        self,
    ) -> None:
        ...

    def check_key_exists(self, *, key: str, owner_id: str) -> bool:
        return (key, owner_id) in self.games  # type: ignore

    def get_title(
        self,
        *,
        name: str,
        create: bool = True,
    ) -> Title:
        title = Title(name=name)
        if title not in self.titles:
            if create:
                self.titles.add(title)
                self.session.add(title)
            else:
                raise TitleDoesNotExist()
        return title

    def add_key(
        self,
        *,
        owner_id: str,
        platform: Platform,
        title_name: str,
        key: str,
    ) -> Game:
        title = self.get_title(name=title_name)
        new_game = Game(platform=platform, title=title, key=key, owner_id=owner_id)
        if new_game in self.games:
            raise KeyAlreadyExists
        self.session.add(new_game)
        self.games.add(new_game)
        return new_game

    def remove_key(
        self,
        *,
        key: str,
        owner_id: str,
    ) -> tuple[Title, str]:
        try:
            game = next(
                game
                for game in self.games
                if game.key == key and game.owner_id == owner_id
            )
            self.games.remove(game)
            return game.title, game.key
        except StopIteration:
            raise KeyDoesNotExist()
