from __future__ import annotations

from sqlmodel import Field, Relationship, SQLModel

from src.apps.discord.domain.models import Guild, Member


class MemberToGuildLink(SQLModel, table=True):
    member_pk: int | None = Field(None, foreign_key="members.pk", primary_key=True)
    guild_pk: int | None = Field(None, foreign_key="guilds.pk", primary_key=True)


class GuildInDB(Guild, table=True):
    __tablename__ = "guilds"
    pk: int | None = Field(default=None, primary_key=True)
    members: list["MemberInDB"] = Relationship(  # type: ignore
        back_populates="guilds", link_model=MemberToGuildLink
    )


class MemberInDB(Member, table=True):
    __tablename__ = "members"
    pk: int | None = Field(default=None, primary_key=True)
    guilds: list["GuildInDB"] = Relationship(  # type: ignore
        back_populates="members", link_model=MemberToGuildLink
    )
