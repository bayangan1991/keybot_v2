from datetime import timedelta, datetime
from itertools import groupby
from typing import Literal

from keybot_v2.config import settings
from keybot_v2.domain.models import BaseGame, Platform, BaseTitle, BaseMember
from keybot_v2.domain.expections import KeyExistsError
from keybot_v2.repositories.types import BaseRepository


def add_key(
    *,
    member_id: str,
    title_name: str,
    platform: Platform,
    key: str,
    repo: BaseRepository,
) -> BaseGame:
    session = repo.get_session()
    member = repo.get_member(session=session, id=member_id)

    if not repo.check_key_exists(session=session, key=key):
        title = repo.get_title(session=session, name=title_name)
        new_game = repo.add_key(
            session=session, member=member, platform=platform, title=title, key=key
        )
        session.commit()
        return new_game
    else:
        raise KeyExistsError()


def remove_key(
    *,
    member_id: str,
    key: str,
    repo: BaseRepository,
) -> tuple[BaseTitle, str]:
    session = repo.get_session()
    member = repo.get_member(session=session, id=member_id)

    popped_key = repo.remove_key(session=session, member=member, key=key)
    session.commit()
    return popped_key


def list_games(
    *, target_id: str, target_type: Literal["member", "guild"], repo: BaseRepository
) -> dict[BaseTitle, list[BaseGame]]:
    session = repo.get_session()

    match target_type:
        case "member":
            target = repo.get_member(session=session, id=target_id)
        case "guild":
            target = repo.get_guild(session=session, id=target_id)

    games = repo.get_games(session=session, target=target)

    def sort_key(game: BaseGame) -> BaseTitle:
        return game.title

    return {
        title: list(games)
        for title, games in groupby(sorted(games, key=sort_key), sort_key)
    }


def join_guild(*, member_id: str, guild_id: str, repo: BaseRepository) -> None:
    session = repo.get_session()
    member = repo.get_member(session=session, id=member_id)
    guild = repo.get_guild(session=session, id=guild_id)

    repo.add_member_to_guild(session=session, member=member, guild=guild)

    session.commit()


def leave_guild(*, member_id: str, guild_id: str, repo: BaseRepository) -> None:
    session = repo.get_session()
    member = repo.get_member(session=session, id=member_id)
    guild = repo.get_guild(session=session, id=guild_id)

    repo.remove_member_from_guild(session=session, member=member, guild=guild)

    session.commit()


def claim_title(
    *,
    member_id: str,
    title_name: str,
    platform: Platform,
    guild_id: str,
    repo: BaseRepository,
) -> BaseGame:
    session = repo.get_session()

    member = repo.get_member(session=session, id=member_id)

    title = repo.get_title(session=session, name=title_name, create=False)

    guild = repo.get_guild(session=session, id=guild_id)

    claimed_title = repo.claim_title(
        session=session, member=member, title=title, guild=guild, platform=platform
    )

    session.commit()
    return claimed_title


def member_can_claim(*, member: BaseMember) -> bool:
    if not member.last_claim:
        return True
    else:
        return (
            member.last_claim + timedelta(minutes=settings.wait_period)
            < datetime.utcnow()
        )
