import os
import dotenv

from src.core.exception import EnvNotFoundError


dotenv.load_dotenv()


def _get_env(name: str, default_=None, required: bool = False):
    var = os.environ.get(name) or default_
    if required and not var:
        raise EnvNotFoundError(name)
    return var


BOT_TOKEN = _get_env("BOT_TOKEN")

LIMIT_TITLE_GAME = _get_env("LIMIT_TITLE_GAME", 40)  # symbols
LIMIT_DESCRIPTION_GAME = _get_env("LIMIT_DESCRIPTION_GAME", 100)  # symbols
LIMIT_CACHE_STORAGE = _get_env("LIMIT_CACHE_STORAGE", 60)  # seconds
LIMIT_STORAGE_GAME = _get_env("LIMIT_CACHE_STORAGE", 100)  # quantity game in storage

POSTGRES_USER = _get_env("POSTGRES_USER", required=True)
POSTGRES_PASSWORD = _get_env("POSTGRES_PASSWORD", required=True)
POSTGRES_DB = _get_env("POSTGRES_DB", required=True)
POSTGRES_HOST = _get_env("POSTGRES_HOST", required=True)
POSTGRES_PORT = _get_env("POSTGRES_PORT", required=True)
POSTGRES_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
APP_MIGRATIONS_PATH = os.path.abspath("migrations")

CSV_SPLITTER = _get_env("CSV_SPLITTER", ";")
