from __future__ import annotations

from pathlib import Path
from typing import Generator, Optional

from sqlmodel import Session, SQLModel, create_engine


def init_db(database_url: str, echo: bool = False) -> None:
    engine = create_engine(database_url, echo=echo)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
