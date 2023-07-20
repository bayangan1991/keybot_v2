from typing import Any

from pydantic import BaseModel

from keybot_v2.apps.discord.domain.expections import FailedToJoin, FailedToLeave
from keybot_v2.apps.discord.domain.models import Guild, Member
from keybot_v2.apps.discord.repositories.types import BaseSession, DiscordRepository


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


class FakeRepository(DiscordRepository[FakeSession]):
    guilds: dict[str, set[Member]]

    def __init__(
        self,
        session: FakeSession,
        *args: Any,
        guilds: dict[str, Guild] | None = None,
        **kwargs: Any,
    ) -> None:
        self.session = session
        self.guilds = guilds or {}

    def get_member(self, *, id: str) -> Member:
        return Member(id=id)

    def get_guild(self, *, id: str) -> Guild:
        if not (guild := self.guilds.get(id)):
            guild = Guild(id=id)
            self.guilds[id] = set()
            self.session.add(guild)

        return guild

    def add_member_to_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        member = self.get_member(id=member_id)
        self.get_guild(id=guild_id)
        if member not in self.guilds[guild_id]:
            self.guilds[guild_id].add(member)
        else:
            raise FailedToJoin()

    def remove_member_from_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        member = self.get_member(id=member_id)
        self.get_guild(id=guild_id)
        if member in self.guilds[guild_id]:
            self.guilds[guild_id].remove(member)
        else:
            raise FailedToLeave()

    def get_guild_members(self, guild_id: str) -> set[Member]:
        return self.guilds[guild_id]
