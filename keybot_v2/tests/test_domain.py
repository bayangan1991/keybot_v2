from datetime import datetime, timedelta

import pytest

from keybot_v2.config import settings
from keybot_v2.domain.expections import UnableToClaimError
from keybot_v2.domain.services import (
    add_key,
    remove_key,
    list_games,
    join_guild,
    leave_guild,
    claim_title,
)

# from keybot_v2.repositories.fake.repo import FakeRepository as Repo

from keybot_v2.repositories.db.repo import SQLModelRepository as Repo

GAME_NAME = "Game Name"


def test_can_add_key_to_member() -> None:
    repo = Repo()
    session = repo.get_session()
    member = repo.get_member(session=session, id="test")
    session.commit()

    add_key(
        member_id=member.id,
        title_name=GAME_NAME,
        platform="steam",
        key="123",
        repo=repo,
    )

    assert len(member.games) == 1
    assert member.games[0].title.name == GAME_NAME


def test_can_remove_key_from_member() -> None:
    repo = Repo()
    session = repo.get_session()
    title = repo.get_title(session=session, name=GAME_NAME)
    member = repo.get_member(session=session, id="test")
    test_key = "123"
    repo.add_key(
        session=session,
        member=member,
        platform="steam",
        title=title,
        key=test_key,
    )

    session.add(member)
    session.commit()

    popped_title, key = remove_key(member_id=member.id, key=test_key, repo=repo)

    assert test_key == key
    assert popped_title not in member.games
    assert not repo.check_key_exists(session=session, key=test_key)


def test_member_can_list_own_keys() -> None:
    repo = Repo()

    session = repo.get_session()

    member = repo.get_member(session=session, id="test")

    title = repo.get_title(session=session, name=GAME_NAME)

    game_1 = repo.add_key(
        session=session,
        member=member,
        title=title,
        key="123",
        platform="steam",
    )
    game_2 = repo.add_key(
        session=session,
        member=member,
        title=title,
        key="234",
        platform="steam",
    )

    session.add(game_1)
    session.add(game_2)
    session.commit()

    result = list_games(target_id=member.id, target_type="member", repo=repo)

    assert title in result
    assert result[title] == [game_1, game_2]


def test_member_can_change_sharing_status() -> None:
    repo = Repo()

    session = repo.get_session()

    member_1 = repo.get_member(session=session, id="test-member-1")
    member_2 = repo.get_member(session=session, id="test-member-2")

    title = repo.get_title(session=session, name=GAME_NAME)
    guild = repo.get_guild(session=session, id="test-guild")

    game_1 = repo.add_key(
        session=session,
        member=member_1,
        title=title,
        key="123",
        platform="steam",
    )
    game_2 = repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="234",
        platform="steam",
    )

    session.add(game_1)
    session.add(game_2)
    session.commit()

    # Test that unshared games are not visible
    result = list_games(target_id=guild.id, target_type="guild", repo=repo)

    assert title not in result

    # Test that games are visible when shared
    join_guild(member_id=member_1.id, guild_id=guild.id, repo=repo)
    join_guild(member_id=member_2.id, guild_id=guild.id, repo=repo)

    result = list_games(target_id=guild.id, target_type="guild", repo=repo)

    assert title in result
    assert set(result[title]) == {game_1, game_2}

    # Test that games are removed when a member leaves
    leave_guild(member_id=member_1.id, guild_id=guild.id, repo=repo)
    result = list_games(target_id=guild.id, target_type="guild", repo=repo)

    assert title in result
    assert result[title] == [game_2]


def test_member_can_claim_title() -> None:
    repo = Repo()

    session = repo.get_session()

    member_1 = repo.get_member(session=session, id="test-member-1")
    member_2 = repo.get_member(session=session, id="test-member-2")

    title = repo.get_title(session=session, name=GAME_NAME)
    guild = repo.get_guild(session=session, id="test-guild")

    repo.add_member_to_guild(session=session, member=member_1, guild=guild)
    repo.add_member_to_guild(session=session, member=member_2, guild=guild)

    game_1 = repo.add_key(
        session=session,
        member=member_1,
        title=title,
        key="123",
        platform="steam",
    )
    game_2 = repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="234",
        platform="steam",
    )

    session.add(game_1)
    session.add(game_2)
    session.commit()
    session.refresh(game_1)
    session.refresh(game_2)

    claimed_game = claim_title(
        member_id=member_1.id,
        title_name=title.name,
        platform="steam",
        guild_id=guild.id,
        repo=repo,
    )

    assert claimed_game == game_1
    session.refresh(member_1)
    assert member_1.last_claim is None

    claimed_game = claim_title(
        member_id=member_1.id,
        title_name=title.name,
        platform="steam",
        guild_id=guild.id,
        repo=repo,
    )

    assert claimed_game == game_2
    session.refresh(member_1)
    assert member_1.last_claim is not None


def test_member_cant_claim_within_wait_period() -> None:
    repo = Repo()

    session = repo.get_session()

    member_1 = repo.get_member(session=session, id="test-member-1")
    member_2 = repo.get_member(session=session, id="test-member-2")

    title = repo.get_title(session=session, name=GAME_NAME)
    guild = repo.get_guild(session=session, id="test-guild")

    repo.add_member_to_guild(session=session, member=member_1, guild=guild)
    repo.add_member_to_guild(session=session, member=member_2, guild=guild)

    repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="123",
        platform="steam",
    )
    repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="234",
        platform="steam",
    )

    session.commit()

    claim_title(
        member_id=member_1.id,
        title_name=title.name,
        platform="steam",
        guild_id=guild.id,
        repo=repo,
    )

    session.refresh(member_1)

    assert member_1.last_claim is not None

    with pytest.raises(UnableToClaimError):
        claim_title(
            member_id=member_1.id,
            title_name=title.name,
            platform="steam",
            guild_id=guild.id,
            repo=repo,
        )


def test_member_can_claim_after_wait_period() -> None:
    repo = Repo()

    session = repo.get_session()

    member_1 = repo.get_member(session=session, id="test-member-1")
    member_2 = repo.get_member(session=session, id="test-member-2")

    title = repo.get_title(session=session, name=GAME_NAME)
    guild = repo.get_guild(session=session, id="test-guild")

    repo.add_member_to_guild(session=session, member=member_1, guild=guild)
    repo.add_member_to_guild(session=session, member=member_2, guild=guild)

    repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="123",
        platform="steam",
    )
    repo.add_key(
        session=session,
        member=member_2,
        title=title,
        key="234",
        platform="steam",
    )

    fake_claim_date = datetime.utcnow() - timedelta(minutes=settings.wait_period + 5)
    member_1.last_claim = fake_claim_date

    session.add(member_1)
    session.commit()

    claim_title(
        member_id=member_1.id,
        title_name=title.name,
        platform="steam",
        guild_id=guild.id,
        repo=repo,
    )

    session.refresh(member_1)

    assert member_1.last_claim != fake_claim_date
