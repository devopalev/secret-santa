import asyncio
import logging

from telegram import Update
from telegram.ext import Application, ContextTypes

from src.core import config
from src import tg
from src import db
from src.tg.utils.context import CustomContext, MemoryCustomContext


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot."""

    if config.POSTGRES_DSN:
        db.setup()
        context_types = ContextTypes(context=CustomContext)
    else:
        context_types = ContextTypes(context=MemoryCustomContext)
        logger.warning("The <MemoryCustomContext> is used for development only. Games are stored in RAM!")
    app = Application.builder().token(config.BOT_TOKEN).context_types(context_types).build()

    await tg.setup(app)

    async with app:  # Calls `initialize` and `shutdown`
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        await asyncio.Future()  # endless waiting


if __name__ == "__main__":
    asyncio.run(main())
