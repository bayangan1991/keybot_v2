from collections.abc import Collection
from datetime import datetime, timedelta
from itertools import chain
from typing import Any

from pydantic import BaseModel

from keybot_v2.domain.expections import (
    KeyNotFoundError,
    GuildMembershipError,
    TitleDoesNotExistError,
    UnableToClaimError,
)

from .models import FakeTitle, FakeGame, FakeMember, FakeGuild
from keybot_v2.domain.models import Platform
from keybot_v2.repositories.types import BaseRepository, BaseSession
from ...config import settings
from keybot_v2.domain.services import member_can_claim


class FakeSession(BaseSession):
    def __init__(self) -> None:
        self.committed: bool = False
        self.items: set[BaseModel] = set()

    def commit(self) -> None:
        self.committed = True

    def add(self, instance: Any, _warn: bool = False) -> None:
        self.items.add(instance)

    def refresh(self, instance: Any) -> None:
        ...


class FakeRepository(BaseRepository):
    titles: set[FakeTitle]
    games: dict[str, FakeGame]
    members: dict[str, FakeMember]
    guilds: dict[str, FakeGuild]

    def __init__(
        self,
        *,
        games: dict[str, FakeGame] | None = None,
        titles: set[FakeTitle] | None = None,
        members: dict[str, FakeMember] | None = None,
        guilds: dict[str, FakeGuild] | None = None,
    ) -> None:
        self.titles = titles or set()
        self.games = games or {}
        self.members = members or {}
        self.guilds = guilds or {}

    def get_session(self) -> FakeSession:
        return FakeSession()

    def check_key_exists(self, *, session: FakeSession, key: str) -> bool:
        return key in self.games

    def get_title(
        self,
        *,
        session: FakeSession,
        name: str,
        create: bool = True,
    ) -> FakeTitle:
        title = FakeTitle(name=name)
        if title not in self.titles:
            if create:
                self.titles.add(title)
                session.add(title)
            else:
                raise TitleDoesNotExistError()
        return title

    def get_member(self, *, session: FakeSession, id: str) -> FakeMember:
        if not (member := self.members.get(id)):
            member = FakeMember(id=id, games=[])
            self.members[id] = member
            session.add(member)

        return member

    def get_guild(self, *, session: FakeSession, id: str) -> FakeGuild:
        if not (guild := self.guilds.get(id)):
            guild = FakeGuild(id=id, members=set())
            self.guilds[id] = guild
            session.add(guild)

        return guild

    def check_member_has_key(
        self, *, session: FakeSession, member: FakeMember, key: str
    ) -> bool:
        return len(list(filter(lambda game: game.key == key, member.games))) == 1

    def add_key(
        self,
        *,
        session: FakeSession,
        member: FakeMember,
        platform: Platform,
        title: FakeTitle,
        key: str,
    ) -> FakeGame:
        new_game = FakeGame(platform=platform, title=title, key=key, owner=member)
        member.games.append(new_game)
        session.add(new_game)
        return new_game

    def remove_key(
        self, *, session: FakeSession, key: str, member: FakeMember
    ) -> tuple[FakeTitle, str]:
        if self.check_member_has_key(session=session, member=member, key=key):
            game = next(game for game in member.games if game.key == key)
            member.games.remove(game)
            return game.title, game.key
        raise KeyNotFoundError()

    def get_games(
        self,
        *,
        session: FakeSession,
        target: FakeMember | FakeGuild,
    ) -> Collection[FakeGame]:
        match target:
            case FakeMember(games=games):
                return games
            case FakeGuild(members=members):
                return list(chain(*[member.games for member in members]))

    def add_member_to_guild(
        self,
        *,
        session: FakeSession,
        member: FakeMember,
        guild: FakeGuild,
    ) -> None:
        if member not in guild.members:
            guild.members.add(member)
        else:
            raise GuildMembershipError()

    def remove_member_from_guild(
        self,
        *,
        session: FakeSession,
        member: FakeMember,
        guild: FakeGuild,
    ) -> None:
        if member in guild.members:
            guild.members.remove(member)
        else:
            raise GuildMembershipError()

    def claim_title(
        self,
        *,
        session: FakeSession,
        member: FakeMember,
        title: FakeTitle,
        platform: Platform,
        guild: FakeGuild,
    ) -> FakeGame:
        try:
            own_key = next(
                game
                for game in member.games
                if game.title == title and game.platform == platform
            )
            member.games.remove(own_key)
            return own_key
        except StopIteration:
            pass

        if not member_can_claim(member=member):
            raise UnableToClaimError()

        available_games = self.get_games(session=session, target=guild)

        try:
            guild_key = next(
                game
                for game in available_games
                if game.title == title and game.platform == platform
            )
            guild_key.owner.games.remove(guild_key)
            member.last_claim = datetime.utcnow()
            return guild_key
        except StopIteration:
            pass
