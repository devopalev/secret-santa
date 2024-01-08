import logging
from enum import Enum, auto

from telegram import Update
from telegram.ext import ConversationHandler

from src.tg.elements import messages
from src.tg.utils.context import CustomContext


logger = logging.getLogger(__name__)


class CreateGameStates(Enum):
    TITLE = auto()
    DESCRIPTION = auto()
    LIST_USERNAME = auto()
    CALENDAR = auto()


async def help_command(update: Update, *args) -> None:
    """Send a message when the command /help is issued."""
    msg = messages.HelpMessage()
    await update.message.reply_text(msg.text, msg.parse_mode)


async def error_handler(update: Update, context: CustomContext):
    try:
        logger.error(msg="Exception while handling Telegram update:", exc_info=context.error)
        await update.effective_chat.send_message("Возникла ошибка :(")
    except Exception as e:
        logger.error(msg="Exception while handling lower-level exception:", exc_info=e)


async def timeout_handle(update: Update, context: CustomContext):
    if update.callback_query:
        await update.callback_query.message.edit_reply_markup()
    context.user_data.clear()
    return ConversationHandler.END


async def unknown_callback(update: Update, *args):
    await update.callback_query.message.edit_reply_markup()
    msg = messages.BadCallbackMessage()
    await update.callback_query.message.reply_text(msg.text, msg.parse_mode)
    return ConversationHandler.END


async def ignore_callback(update: Update, *args):
    await update.callback_query.answer()
