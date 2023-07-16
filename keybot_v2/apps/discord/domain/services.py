from datetime import timedelta, datetime
from itertools import groupby
from typing import Literal

from keybot_v2.config import settings
from .models import BaseGame, Platform, BaseTitle, BaseMember, BaseGuild
from .expections import KeyExistsError
from ..units_of_work.types import DiscordUnitOfWork


def add_key(
    *,
    member_id: str,
    title_name: str,
    platform: Platform,
    key: str,
    uow: DiscordUnitOfWork,
) -> BaseGame:
    member = uow.repo.get_member(id=member_id)

    if not uow.repo.check_key_exists(key=key):
        title = uow.repo.get_title(name=title_name)
        new_game = uow.repo.add_key(
            member=member, platform=platform, title=title, key=key
        )
        return new_game
    else:
        raise KeyExistsError()


def remove_key(
    *,
    member_id: str,
    key: str,
    uow: DiscordUnitOfWork,
) -> tuple[BaseTitle, str]:
    member = uow.repo.get_member(id=member_id)

    popped_key = uow.repo.remove_key(member=member, key=key)
    uow.commit()
    return popped_key


def list_games(
    *,
    target_id: str,
    target_type: Literal["member", "guild"],
    uow: DiscordUnitOfWork,
) -> dict[BaseTitle, list[BaseGame]]:
    target: BaseMember | BaseGuild
    match target_type:
        case "member":
            target = uow.repo.get_member(id=target_id)
        case "guild":
            target = uow.repo.get_guild(id=target_id)

    games = uow.repo.get_games(target=target)

    def sort_key(game: BaseGame) -> BaseTitle:
        return game.title

    return {
        title: list(games)
        for title, games in groupby(sorted(games, key=sort_key), sort_key)
    }


def join_guild(
    *,
    member_id: str,
    guild_id: str,
    uow: DiscordUnitOfWork,
) -> None:
    member = uow.repo.get_member(id=member_id)
    guild = uow.repo.get_guild(id=guild_id)

    uow.repo.add_member_to_guild(member=member, guild=guild)


def leave_guild(
    *,
    member_id: str,
    guild_id: str,
    uow: DiscordUnitOfWork,
) -> None:
    member = uow.repo.get_member(id=member_id)
    guild = uow.repo.get_guild(id=guild_id)

    uow.repo.remove_member_from_guild(member=member, guild=guild)


def claim_title(
    *,
    member_id: str,
    title_name: str,
    platform: Platform,
    guild_id: str,
    uow: DiscordUnitOfWork,
) -> BaseGame:
    member = uow.repo.get_member(id=member_id)

    title = uow.repo.get_title(name=title_name, create=False)

    guild = uow.repo.get_guild(id=guild_id)

    claimed_title = uow.repo.claim_title(
        member=member, title=title, guild=guild, platform=platform
    )

    return claimed_title


def member_can_claim(*, member: BaseMember) -> bool:
    if not member.last_claim:
        return True
    else:
        return (
            member.last_claim + timedelta(minutes=settings.discord.wait_period)
            < datetime.utcnow()
        )
