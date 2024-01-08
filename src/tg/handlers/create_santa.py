from telegram import Update
from telegram.ext import ConversationHandler

from src.core.config import LIMIT_DESCRIPTION_GAME, LIMIT_TITLE_GAME
from src.domain.model import GameSanta
from src.tg.handlers.admin_santa import view_game
from src.tg.utils.context import CustomContext

from src.tg.utils.tg_calendar import TgCalendarKeyboard
from src.tg.utils.tg_calendar import Locale

from src.tg.elements import messages
from src.tg.handlers.common import CreateGameStates


async def request_title(update: Update, context: CustomContext) -> CreateGameStates.TITLE:
    context.game = GameSanta.build_from_user(user=update.effective_user)
    msg = messages.RequestTitleGameMessage()
    await update.message.reply_text(msg.text)
    return CreateGameStates.TITLE


async def change_title(update: Update, context: CustomContext):
    context.game.title = update.message.text[:LIMIT_TITLE_GAME]
    return await request_description(update, context)


async def request_description(update: Update, context: CustomContext) -> CreateGameStates.DESCRIPTION:
    msg = messages.RequestDescriptionGameMessage()
    await update.effective_chat.send_message(msg.text)
    return CreateGameStates.DESCRIPTION


async def change_description(update: Update, context: CustomContext):
    context.game.description = update.message.text[:LIMIT_DESCRIPTION_GAME]
    return await request_date(update, context)


async def request_date(update: Update, context: CustomContext):
    cal = TgCalendarKeyboard(locale=Locale.ru)
    msg = messages.RequestDateGameMessage()
    await update.effective_chat.send_message(msg.text, reply_markup=cal.keyboard)
    return CreateGameStates.CALENDAR


async def handle_calendar(update: Update, context: CustomContext):
    await update.callback_query.answer()
    tg_calendar = TgCalendarKeyboard(locale=Locale.ru)
    changed = tg_calendar.handle(update.callback_query.data)
    if changed:
        if tg_calendar.selected_date:
            context.game.date_finish = tg_calendar.selected_date
            await context.db_storage.save(context.game)

            await view_game(update, context, game=context.game)
            event = messages.DateGameChangedMessage(context.game.title, context.game.date_finish)
            context.send_event(event, context.game.players)
            del context.game
            return ConversationHandler.END
        await update.callback_query.message.edit_reply_markup(tg_calendar.keyboard)
