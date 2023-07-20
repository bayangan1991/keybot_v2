from __future__ import annotations

from typing import Callable

import pytest
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from keybot_v2.apps.discord.domain.services import (
    join_guild,
    leave_guild,
)
from keybot_v2.apps.discord.unit_of_work.sqlmodeluow import DBUnitOfWork
from keybot_v2.config import settings

SessionFactory = Callable[..., Session]


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    from ..repositories.db.models import (  # noqa
        GuildInDB,
        MemberInDB,
        MemberToGuildLink,
    )

    engine = create_engine("sqlite:///:memory:", echo=settings.db.echo)
    SQLModel.metadata.create_all(engine)

    return sessionmaker(bind=engine, class_=Session)


def test_member_can_join_and_leave_guild(
    session_factory: SessionFactory,
) -> None:
    with DBUnitOfWork(session_factory=session_factory) as uow:
        guild = uow.repo.get_guild(id="test")
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        uow.commit()

        # Test that games are visible when shared
        join_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)
        join_guild(member_id=member_2.id, guild_id=guild.id, uow=uow)

        assert member_1 in guild.members
        assert member_2 in guild.members

        # Test that games are removed when a member leaves
        leave_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)

        assert member_1 not in guild.members
        assert member_2 in guild.members
