from datetime import datetime, timedelta

from sqlalchemy import text, func
from sqlmodel import create_engine, Session, select, SQLModel

from .models import TitleInDB, GameInDB, MemberInDB, GuildInDB
from keybot_v2.domain.models import Platform
from keybot_v2.repositories.types import BaseRepository
from keybot_v2.domain.expections import TitleDoesNotExistError, UnableToClaimError
from keybot_v2.domain.services import member_can_claim


class SQLModelRepository(BaseRepository):
    def __init__(self, *, uri: str = "sqlite:///:memory:", echo: bool = False):
        from .models import GameInDB, TitleInDB, MemberInDB  # noqa

        self.uri = uri
        self.engine = create_engine(self.uri, echo=echo)
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return Session(self.engine)

    def check_key_exists(self, *, session: Session, key: str) -> bool:

        statement = select(GameInDB).where(GameInDB.key == key)

        return session.exec(statement).first() is not None

    def check_member_has_key(self, *, session: Session, member: MemberInDB, key: str):
        statement = select(GameInDB).where(
            GameInDB.owner_pk == member.pk, GameInDB.key == key
        )

        return session.exec(statement).first() is not None

    def get_title(
        self,
        *,
        session: Session,
        name: str,
        create: bool = True,
    ) -> TitleInDB:

        statement = select(TitleInDB).where(TitleInDB.name == name)

        if title := session.exec(statement).first():
            return title

        if create:
            new_title = TitleInDB(name=name)
            return new_title

        raise TitleDoesNotExistError()

    def get_member(self, *, session: Session, id: str) -> MemberInDB:
        statement = select(MemberInDB).where(MemberInDB.id == id)

        if member := session.exec(statement).first():
            return member

        new_member = MemberInDB(id=id)
        session.add(new_member)
        return new_member

    def get_guild(
        self,
        *,
        session: Session,
        id: str,
    ) -> GuildInDB:
        statement = select(GuildInDB).where(GuildInDB.id == id)

        if guild := session.exec(statement).first():
            return guild

        new_guild = GuildInDB(id=id)
        session.add(new_guild)
        return new_guild

    def add_key(
        self,
        *,
        session: Session,
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
        session.add(new_game)
        return new_game

    def remove_key(
        self,
        session: Session,
        member: MemberInDB,
        key: str,
    ) -> tuple[TitleInDB, str]:
        statement = select(GameInDB).where(
            GameInDB.key == key, GameInDB.owner_pk == member.pk
        )
        removed_game = session.exec(statement).one()

        session.delete(removed_game)

        return removed_game.title, removed_game.key

    def add_member_to_guild(
        self,
        *,
        session: Session,
        member: MemberInDB,
        guild: GuildInDB,
    ) -> None:
        if member not in guild.members:
            member.guilds.append(guild)
            session.add(member)

    def remove_member_from_guild(
        self,
        *,
        session: Session,
        member: MemberInDB,
        guild: GuildInDB,
    ) -> None:
        if member in guild.members:
            member.guilds.remove(guild)
            session.add(member)

    def get_games(
        self,
        *,
        session: Session,
        target: MemberInDB | GuildInDB,
    ) -> list[GameInDB]:
        match target:
            case MemberInDB(games=games):
                return games
            case GuildInDB() as guild:
                statement = select(GameInDB).where(
                    GameInDB.owner_pk.in_(
                        select(MemberInDB.pk).where(MemberInDB.guilds.contains(guild))
                    )
                )
                return session.exec(statement).all()

    def claim_title(
        self,
        *,
        session: Session,
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

        if own_game := session.exec(statement).first():
            session.delete(own_game)
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

        if other_game := session.exec(statement).first():
            session.delete(other_game)
            member.last_claim = datetime.utcnow()
            session.add(member)
            return other_game

        raise UnableToClaimError()
