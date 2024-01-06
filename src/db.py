import asyncpg
from asyncpg import Connection

from yoyo import read_migrations
from yoyo import get_backend

from src.core import config


async def connection() -> Connection:
    return await asyncpg.connect(config.POSTGRES_DSN)


def setup():
    backend = get_backend(config.POSTGRES_DSN)
    migrations = read_migrations(config.APP_MIGRATIONS_PATH)

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
