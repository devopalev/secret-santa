import os
import dotenv

from src.core.exception import EnvNotFoundError


dotenv.load_dotenv()


try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]

    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
    POSTGRES_PORT = os.environ["POSTGRES_PORT"]

    LIMIT_TITLE_GAME = os.environ.get("LIMIT_TITLE_GAME", 40)  # symbols
    LIMIT_DESCRIPTION_GAME = os.environ.get("LIMIT_DESCRIPTION_GAME", 100)  # symbols
    LIMIT_CACHE_STORAGE = os.environ.get("LIMIT_CACHE_STORAGE", 60)  # seconds
    LIMIT_STORAGE_GAME = os.environ.get("LIMIT_CACHE_STORAGE", 100)  # quantity game in storage

    POSTGRES_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    APP_MIGRATIONS_PATH = os.path.abspath("migrations")

    CSV_SPLITTER = os.environ.get("CSV_SPLITTER", ";")
except KeyError as err:
    raise EnvNotFoundError(err.args[0]) from err
