from typing import Any

from sqlmodel import Session, select

from ..types import DiscordRepository
from .models import GuildInDB, MemberInDB


class SQLModelRepository(DiscordRepository[Session]):
    def __init__(self, session: Session, *args: Any, **kwargs: Any):
        self.session = session

    def get_member(self, *, id: str) -> MemberInDB:
        statement = select(MemberInDB).where(MemberInDB.id == id)

        if member := self.session.exec(statement).first():
            return member

        new_member = MemberInDB(id=id)
        self.session.add(new_member)
        return new_member

    def get_guild(
        self,
        *,
        id: str,
    ) -> GuildInDB:
        statement = select(GuildInDB).where(GuildInDB.id == id)

        if guild := self.session.exec(statement).first():
            return guild

        new_guild = GuildInDB(id=id)
        self.session.add(new_guild)
        return new_guild

    def add_member_to_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        member = self.get_member(id=member_id)
        guild = self.get_guild(id=guild_id)
        if member not in guild.members:
            member.guilds.append(guild)
            self.session.add(member)

    def remove_member_from_guild(
        self,
        *,
        member_id: str,
        guild_id: str,
    ) -> None:
        member = self.get_member(id=member_id)
        guild = self.get_guild(id=guild_id)
        if member in guild.members:
            member.guilds.remove(guild)
            self.session.add(member)

    def get_guild_members(self, guild_id: str) -> list[MemberInDB]:
        return self.get_guild(id=guild_id).members
