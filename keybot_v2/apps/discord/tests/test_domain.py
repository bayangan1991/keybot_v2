from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session, SQLModel

from keybot_v2.apps.discord.units_of_work.sqlmodeluow import SQLModelUnitOfWork
from keybot_v2.config import settings
from keybot_v2.apps.discord.domain.expections import UnableToClaimError
from keybot_v2.apps.discord.domain.services import (
    add_key,
    remove_key,
    list_games,
    join_guild,
    leave_guild,
    claim_title,
)

# from keybot_v2.apps.discord.repositories.fake.repo import FakeRepository as Repo


GAME_NAME = "Game Name"


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    from ..repositories.db.models import GameInDB, TitleInDB, MemberInDB  # noqa

    engine = create_engine("sqlite:///:memory:", echo=settings.db.echo)

    SQLModel.metadata.create_all(engine)

    return sessionmaker(bind=engine, class_=Session)


def test_can_add_key_to_member(session_factory: sessionmaker[Session]) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        member = uow.repo.get_member(id="test")

        uow.commit()
        uow.session.refresh(member)

        add_key(
            member_id=member.id,
            title_name=GAME_NAME,
            platform="steam",
            key="123",
            uow=uow,
        )

        uow.session.refresh(member)

    assert len(member.games) == 1
    assert member.games[0].title.name == GAME_NAME


def test_can_remove_key_from_member(session_factory: sessionmaker[Session]) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        title = uow.repo.get_title(name=GAME_NAME)
        member = uow.repo.get_member(id="test")
        test_key = "123"
        uow.repo.add_key(
            member=member,
            platform="steam",
            title=title,
            key=test_key,
        )

        uow.commit()

        popped_title, key = remove_key(member_id=member.id, key=test_key, uow=uow)

        assert test_key == key
        assert popped_title not in member.games
        assert not uow.repo.check_key_exists(key=test_key)


def test_member_can_list_own_keys(session_factory: sessionmaker[Session]) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        title = uow.repo.get_title(name=GAME_NAME)
        member = uow.repo.get_member(id="test")

        game_1 = uow.repo.add_key(
            member=member,
            title=title,
            key="123",
            platform="steam",
        )
        game_2 = uow.repo.add_key(
            member=member,
            title=title,
            key="234",
            platform="steam",
        )

        uow.session.add(game_1)
        uow.session.add(game_2)
        uow.commit()

        result = list_games(target_id=member.id, target_type="member", uow=uow)

    assert title in result
    assert result[title] == [game_1, game_2]


def test_member_can_change_sharing_status(
    session_factory: sessionmaker[Session],
) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        title = uow.repo.get_title(name=GAME_NAME)
        guild = uow.repo.get_guild(id="test-guild")

        game_1 = uow.repo.add_key(
            member=member_1,
            title=title,
            key="123",
            platform="steam",
        )
        game_2 = uow.repo.add_key(
            member=member_2,
            title=title,
            key="234",
            platform="steam",
        )

        uow.session.add(game_1)
        uow.session.add(game_2)
        uow.commit()

        # Test that unshared games are not visible
        result = list_games(target_id=guild.id, target_type="guild", uow=uow)

        assert title not in result

        # Test that games are visible when shared
        join_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)
        join_guild(member_id=member_2.id, guild_id=guild.id, uow=uow)

        result = list_games(target_id=guild.id, target_type="guild", uow=uow)

        assert title in result
        assert set(result[title]) == {game_1, game_2}

        # Test that games are removed when a member leaves
        leave_guild(member_id=member_1.id, guild_id=guild.id, uow=uow)
        result = list_games(target_id=guild.id, target_type="guild", uow=uow)

        assert title in result
        assert result[title] == [game_2]


def test_member_can_claim_title(session_factory: sessionmaker[Session]) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        title = uow.repo.get_title(name=GAME_NAME)
        guild = uow.repo.get_guild(id="test-guild")

        uow.repo.add_member_to_guild(member=member_1, guild=guild)
        uow.repo.add_member_to_guild(member=member_2, guild=guild)

        game_1 = uow.repo.add_key(
            member=member_1,
            title=title,
            key="123",
            platform="steam",
        )
        game_2 = uow.repo.add_key(
            member=member_2,
            title=title,
            key="234",
            platform="steam",
        )

        uow.session.add(game_1)
        uow.session.add(game_2)
        uow.commit()
        uow.session.refresh(game_1)
        uow.session.refresh(game_2)

        claimed_game = claim_title(
            member_id=member_1.id,
            title_name=title.name,
            platform="steam",
            guild_id=guild.id,
            uow=uow,
        )
        uow.commit()

        assert claimed_game == game_1
        uow.session.refresh(member_1)
        assert member_1.last_claim is None

        claimed_game = claim_title(
            member_id=member_1.id,
            title_name=title.name,
            platform="steam",
            guild_id=guild.id,
            uow=uow,
        )

        uow.commit()

        assert claimed_game == game_2
        uow.session.refresh(member_1)
        assert member_1.last_claim is not None


def test_member_cant_claim_within_wait_period(
    session_factory: sessionmaker[Session],
) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        title = uow.repo.get_title(name=GAME_NAME)
        guild = uow.repo.get_guild(id="test-guild")

        uow.repo.add_member_to_guild(member=member_1, guild=guild)
        uow.repo.add_member_to_guild(member=member_2, guild=guild)

        uow.repo.add_key(
            member=member_2,
            title=title,
            key="123",
            platform="steam",
        )
        uow.repo.add_key(
            member=member_2,
            title=title,
            key="234",
            platform="steam",
        )

        uow.commit()

        claim_title(
            member_id=member_1.id,
            title_name=title.name,
            platform="steam",
            guild_id=guild.id,
            uow=uow,
        )
        uow.commit()

        uow.session.refresh(member_1)

        assert member_1.last_claim is not None

        with pytest.raises(UnableToClaimError):
            claim_title(
                member_id=member_1.id,
                title_name=title.name,
                platform="steam",
                guild_id=guild.id,
                uow=uow,
            )


def test_member_can_claim_after_wait_period(
    session_factory: sessionmaker[Session],
) -> None:
    with SQLModelUnitOfWork(session_factory=session_factory) as uow:
        member_1 = uow.repo.get_member(id="test-member-1")
        member_2 = uow.repo.get_member(id="test-member-2")

        title = uow.repo.get_title(name=GAME_NAME)
        guild = uow.repo.get_guild(id="test-guild")

        uow.repo.add_member_to_guild(member=member_1, guild=guild)
        uow.repo.add_member_to_guild(member=member_2, guild=guild)

        uow.repo.add_key(
            member=member_2,
            title=title,
            key="123",
            platform="steam",
        )
        uow.repo.add_key(
            member=member_2,
            title=title,
            key="234",
            platform="steam",
        )

        fake_claim_date = datetime.utcnow() - timedelta(
            minutes=settings.discord.wait_period + 5
        )
        member_1.last_claim = fake_claim_date

        uow.session.add(member_1)
        uow.commit()

        claim_title(
            member_id=member_1.id,
            title_name=title.name,
            platform="steam",
            guild_id=guild.id,
            uow=uow,
        )
        uow.commit()

        uow.session.refresh(member_1)

        assert member_1.last_claim != fake_claim_date
