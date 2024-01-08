import os
import dotenv

from src.core.exception import EnvRequiredError


dotenv.load_dotenv()


try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    DEV_MODE = os.environ.get("DEV_MODE", False)

    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

    if all((POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT)):
        POSTGRES_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    elif DEV_MODE:
        POSTGRES_DSN = None
    else:
        raise EnvRequiredError("POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT")

    APP_MIGRATIONS_PATH = os.path.abspath("migrations")

    LIMIT_TITLE_GAME = os.environ.get("LIMIT_TITLE_GAME", 40)  # symbols
    LIMIT_DESCRIPTION_GAME = os.environ.get("LIMIT_DESCRIPTION_GAME", 100)  # symbols
    LIMIT_CACHE_STORAGE = os.environ.get("LIMIT_CACHE_STORAGE", 60)  # seconds
    LIMIT_STORAGE_GAME = os.environ.get("LIMIT_CACHE_STORAGE", 100)  # quantity game in storage

    CSV_SPLITTER = os.environ.get("CSV_SPLITTER", ";")
except KeyError as err:
    raise EnvRequiredError(err.args[0]) from err
