from datetime import datetime
from typing import Any

from sqlmodel import SQLModel


class Guild(SQLModel):
    id: str

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Guild):
            return self.id == other.id
        return NotImplemented


class Member(SQLModel):
    id: str
    last_claim: datetime | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Member):
            return self.id == other.id
        return NotImplemented
