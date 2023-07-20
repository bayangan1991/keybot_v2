from __future__ import annotations

from typing import Callable

import pytest

from src.apps.discord.domain.services import (
    join_guild,
    leave_guild,
)
from src.apps.discord.repositories.fake.repo import FakeSession
from src.apps.discord.unit_of_work.fake import FakeUnitOfWork

SessionFactory = Callable[..., FakeSession]


@pytest.fixture
def session_factory() -> FakeSession:
    return lambda: FakeSession()


def test_member_can_join_and_leave_guild(
    session_factory: SessionFactory,
) -> None:
    with FakeUnitOfWork(session_factory=session_factory) as uow:
        guild = uow.repo.get_guild(id="test")
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        uow.commit()

        # Test that games are visible when shared
        join_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)
        join_guild(member_id=member_2.id, guild_id=guild.id, uow=uow)

        assert member_1 in uow.repo.get_guild_members(guild_id=guild.id)
        assert member_2 in uow.repo.get_guild_members(guild_id=guild.id)

        # Test that games are removed when a member leaves
        leave_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)

        assert member_1 not in uow.repo.get_guild_members(guild_id=guild.id)
        assert member_2 in uow.repo.get_guild_members(guild_id=guild.id)
