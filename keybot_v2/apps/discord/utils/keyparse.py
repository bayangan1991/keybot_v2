import re

from keybot_v2.apps.discord.domain.models import Platform

keyspace: dict[Platform, list[str]] = {
    "gog": [r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$"],
    "steam": [
        r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$",
        r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$",
    ],
    "playstation": [r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$"],
    "origin": [
        r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$"
    ],
    "uplay": [
        r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$",
        r"^[a-z,A-Z,0-9]{3}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$",
    ],
    "url": [r"^http"],
}

_compiled: dict[Platform, list[re.Pattern]] = {
    k: [re.compile(r) for r in v] for k, v in keyspace.items()
}


class BadKeyFormatError(Exception):
    ...


def parse_key(key: str) -> Platform:
    for k, v in _compiled.items():
        for r in v:
            if r.match(key):
                return k

    raise BadKeyFormatError
