from datetime import datetime
from typing import Literal, Protocol, Any


class BaseTitle(Protocol):
    name: str

    def __lt__(self, other: Any) -> bool:
        ...


Platform = Literal["steam", "epic", "url", "gog", "playstation", "origin", "uplay"]


class BaseGame(Protocol):
    platform: Platform
    title: BaseTitle
    key: str


class BaseMember(Protocol):
    id: str
    last_claim: datetime | None


class BaseGuild(Protocol):
    id: str
