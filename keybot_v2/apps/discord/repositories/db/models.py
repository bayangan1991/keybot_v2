from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Any, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from keybot_v2.apps.discord.domain.models import Platform


class TitleInDB(SQLModel, table=True):
    __tablename__: ClassVar[str] = "titles"
    pk: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    games: GameInDB = Relationship()

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, TitleInDB):
            return self.name < other.name
        raise NotImplementedError()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TitleInDB):
            return self.pk == other.pk
        raise NotImplementedError()


class GameInDB(SQLModel, table=True):
    __tablename__: ClassVar[str] = "games"
    if TYPE_CHECKING:
        platform: Platform
    else:
        platform: str
    key: str
    pk: int | None = Field(default=None, primary_key=True)
    title_pk: int = Field(foreign_key="titles.pk")
    title: TitleInDB = Relationship(back_populates="games")
    owner_pk: int = Field(foreign_key="members.pk")
    owner: MemberInDB = Relationship(back_populates="games")

    def __hash__(self) -> int:
        return hash(self.pk)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GameInDB):
            return self.pk == other.pk
        raise NotImplementedError()


class MemberToGuildLink(SQLModel, table=True):
    member_pk: int | None = Field(None, foreign_key="members.pk", primary_key=True)
    guild_pk: int | None = Field(None, foreign_key="guilds.pk", primary_key=True)


class MemberInDB(SQLModel, table=True):
    __tablename__: ClassVar[str] = "members"
    pk: int | None = Field(default=None, primary_key=True)
    id: str
    games: list[GameInDB] = Relationship()
    guilds: list["GuildInDB"] = Relationship(
        back_populates="members", link_model=MemberToGuildLink
    )
    last_claim: datetime | None = None

    def __hash__(self) -> int:
        return hash(self.pk)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MemberInDB):
            return self.pk == other.pk
        raise NotImplementedError()


class GuildInDB(SQLModel, table=True):
    __tablename__: ClassVar[str] = "guilds"
    pk: int | None = Field(default=None, primary_key=True)
    id: str
    members: list[MemberInDB] = Relationship(
        back_populates="guilds", link_model=MemberToGuildLink
    )

    def __hash__(self) -> int:
        return hash(self.pk)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GuildInDB):
            return self.pk == other.pk
        raise NotImplementedError()
