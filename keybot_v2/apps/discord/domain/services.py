from keybot_v2.apps.core.types import BaseSession

from ..unit_of_work.types import DiscordUnitOfWork


def join_guild(
    *,
    member_id: str,
    guild_id: str,
    uow: DiscordUnitOfWork[BaseSession],
) -> None:
    uow.repo.add_member_to_guild(member_id=member_id, guild_id=guild_id)


def leave_guild(
    *,
    member_id: str,
    guild_id: str,
    uow: DiscordUnitOfWork[BaseSession],
) -> None:
    uow.repo.remove_member_from_guild(member_id=member_id, guild_id=guild_id)
