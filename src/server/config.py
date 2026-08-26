import os
from pathlib import Path

import attr

SQLITE_ENV_VAR = "OPENHOST_SQLITE_MAIN"


@attr.s(auto_attribs=True, frozen=True)
class Config:
    database_path: Path


def load_config() -> Config:
    database_path = os.environ.get(SQLITE_ENV_VAR)
    if not database_path:
        raise RuntimeError(
            f"{SQLITE_ENV_VAR} is not set. OpenHost sets it from the [data].sqlite entry in openhost.toml; "
            f"locally, `just run` sets it to .local/main.db."
        )
    return Config(database_path=Path(database_path))
