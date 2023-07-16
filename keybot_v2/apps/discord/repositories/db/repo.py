from datetime import datetime

from sqlalchemy import func
from sqlmodel import Session, select

from .models import TitleInDB, GameInDB, MemberInDB, GuildInDB
from ..types import DiscordRepository
from ...domain.expections import TitleDoesNotExistError, UnableToClaimError
from ...domain.models import Platform
from ...domain.services import member_can_claim


class SQLModelRepository(DiscordRepository[GameInDB, TitleInDB, MemberInDB, GuildInDB]):
    def __init__(self, session: Session):
        self.session = session

    def check_key_exists(self, *, key: str) -> bool:
        statement = select(GameInDB).where(GameInDB.key == key)

        return self.session.exec(statement).first() is not None

    def check_member_has_key(
        self,
        *,
        member: MemberInDB,
        key: str,
    ) -> bool:
        statement = select(GameInDB).where(
            GameInDB.owner_pk == member.pk, GameInDB.key == key
        )

        return self.session.exec(statement).first() is not None

    def get_title(
        self,
        *,
        name: str,
        create: bool = True,
    ) -> TitleInDB:
        statement = select(TitleInDB).where(TitleInDB.name == name)

        if title := self.session.exec(statement).first():
            return title

        if create:
            new_title = TitleInDB(name=name)
            return new_title

        raise TitleDoesNotExistError()

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

    def add_key(
        self,
        *,
        member: MemberInDB,
        platform: Platform,
        title: TitleInDB,
        key: str,
    ) -> GameInDB:
        new_game = GameInDB(
            owner=member,
            platform=platform,
            title=title,
            key=key,
        )  # type: ignore
        self.session.add(new_game)
        return new_game

    def remove_key(
        self,
        *,
        member: MemberInDB,
        key: str,
    ) -> tuple[TitleInDB, str]:
        statement = select(GameInDB).where(
            GameInDB.key == key, GameInDB.owner_pk == member.pk
        )
        removed_game = self.session.exec(statement).one()

        self.session.delete(removed_game)

        return removed_game.title, removed_game.key

    def add_member_to_guild(
        self,
        *,
        member: MemberInDB,
        guild: GuildInDB,
    ) -> None:
        if member not in guild.members:
            member.guilds.append(guild)
            self.session.add(member)

    def remove_member_from_guild(
        self,
        *,
        member: MemberInDB,
        guild: GuildInDB,
    ) -> None:
        if member in guild.members:
            member.guilds.remove(guild)
            self.session.add(member)

    def get_games(self, *, target: MemberInDB | GuildInDB) -> list[GameInDB]:
        match target:
            case MemberInDB(games=games):
                return games
            case GuildInDB() as guild:
                statement = select(GameInDB).where(
                    GameInDB.owner_pk.in_(
                        select(MemberInDB.pk).where(MemberInDB.guilds.contains(guild))
                    )
                )
                return self.session.exec(statement).all()

    def claim_title(
        self,
        *,
        member: MemberInDB,
        title: TitleInDB,
        platform: Platform,
        guild: GuildInDB,
    ) -> GameInDB:
        statement = select(GameInDB).where(
            GameInDB.owner == member,
            GameInDB.title == title,
            GameInDB.platform == platform,
        )

        if own_game := self.session.exec(statement).first():
            self.session.delete(own_game)
            return own_game

        if not member_can_claim(member=member):
            raise UnableToClaimError()

        statement = (
            select(GameInDB)
            .where(
                GameInDB.owner_pk.in_(
                    select(MemberInDB.pk).where(MemberInDB.guilds.contains(guild))
                ),
                GameInDB.platform == platform,
                GameInDB.title == title,
            )
            .order_by(func.random())
        )

        if other_game := self.session.exec(statement).first():
            self.session.delete(other_game)
            member.last_claim = datetime.utcnow()
            self.session.add(member)
            return other_game

        raise UnableToClaimError()
