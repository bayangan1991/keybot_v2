from __future__ import annotations

from sqlmodel import Field, Relationship

from src.apps.games.domain.models import Game, Title


class TitleInDB(Title, table=True):
    pk: int | None = Field(default=None, primary_key=True)
    games: list[GameInDB] = Relationship()  # type: ignore


class GameInDB(Game, table=True):
    pk: int | None = Field(default=None, primary_key=True)
    title_pk: int = Field(foreign_key="titles.pk")
    title: TitleInDB = Relationship(back_populates="games")
