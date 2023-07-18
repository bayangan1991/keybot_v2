from typing import Any, Literal

from pydantic import Field
from sqlmodel import SQLModel

Platform = Literal["steam", "epic", "url", "gog", "playstation", "origin", "uplay"]


class Title(SQLModel):
    name: str
    games: list["Game"] = Field(default_factory=list)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Title):
            return self.name < other.name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Title):
            return self.name == other.name
        return NotImplemented


class Game(SQLModel):
    platform: Platform
    title: Title
    key: str
    owner_id: str

    def __hash__(self) -> int:
        return hash(self.key) + hash(self.owner_id)

    def __eq__(self, other: Any) -> bool:
        # Keys are only identical if they have the same owner
        # This is to prevent testing for exiting keys by spam adding keys
        match other:
            case Game(key=other_key, owner_id=other_owner_id):
                return self.key == other_key and self.owner_id == other_owner_id
            case str() as other_key, str() as other_owner_id:
                return self.key == other_key and self.owner_id == other_owner_id
            case _:
                return NotImplemented


Title.update_forward_refs()
