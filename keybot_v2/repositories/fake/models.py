from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from keybot_v2.domain.models import Platform


class FakeTitle(BaseModel):
    name: str

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FakeTitle):
            return self.name == other.name
        raise NotImplementedError

    def __lt__(self, other: Any):
        if isinstance(other, FakeTitle):
            return self.name < other.name
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.name)


class FakeGame(BaseModel):
    platform: Platform
    title: FakeTitle
    owner: FakeMember
    key: str

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FakeGame):
            return self.key == other.key
        return False

    def __hash__(self) -> int:
        return hash(self.key)


class FakeMember(BaseModel):
    id: str
    games: list[FakeGame]
    last_claim: datetime | None = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FakeMember):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


class FakeGuild(BaseModel):
    id: str
    members: set[FakeMember]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FakeMember):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


FakeGame.update_forward_refs()
