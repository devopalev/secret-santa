import warnings

from telegram import BotCommand
from telegram.ext import (ConversationHandler,
                          BaseHandler,
                          MessageHandler,
                          filters,
                          CallbackQueryHandler,
                          CommandHandler,
                          Application)
from telegram.warnings import PTBUserWarning

from src.tg.elements.data import CallbackData
from src.tg.elements.data import CommandData
from src.tg.handlers.common import timeout_handle, ignore_callback
from src.tg.handlers.common import help_command
from src.tg.handlers.common import unknown_callback
from src.tg.handlers.create_santa import CreateGameStates, change_title
from src.tg.handlers.create_santa import request_title
from src.tg.handlers.create_santa import handle_calendar
from src.tg.handlers import create_santa, admin_santa
from src.tg.utils.tg_calendar import CallbackBuilder


def build_handlers() -> list[BaseHandler]:
    unknown_handlers = [CallbackQueryHandler(unknown_callback, pattern=CallbackData.UNKNOWN.regex)]
    timeout_handlers = [CallbackQueryHandler(timeout_handle), MessageHandler(filters.ALL, timeout_handle)]
    calendar_handler = CallbackQueryHandler(handle_calendar, CallbackBuilder.base_cb)
    proxy_view_game = CallbackQueryHandler(admin_santa.proxy_view_game, pattern=CallbackData.VIEW_GAME.regex)

    with warnings.catch_warnings():
        # PTBUserWarning: If 'per_message=False', 'CallbackQueryHandler' will not be tracked for every message.
        # Read this FAQ entry to learn more about the per_* settings:
        # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-Asked-Questions#what-do-the-per_-settings-in-conversationhandler-do.
        warnings.simplefilter("ignore", PTBUserWarning)

        create_game_handler = ConversationHandler(
            entry_points=[CommandHandler(CommandData.CREATE_GAME, request_title)],
            states={
                CreateGameStates.TITLE: [MessageHandler(filters.TEXT, change_title)],
                CreateGameStates.DESCRIPTION: [MessageHandler(filters.TEXT, create_santa.change_description)],
                CreateGameStates.CALENDAR: [calendar_handler],
                ConversationHandler.TIMEOUT: timeout_handlers
            },
            fallbacks=unknown_handlers,
            conversation_timeout=300,
            per_message=False
        )

        request_description_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(admin_santa.request_description,
                                               pattern=CallbackData.CHANGE_DESCRIPTION.regex)],
            states={
                CreateGameStates.DESCRIPTION: [MessageHandler(filters.TEXT, admin_santa.change_description)],
                ConversationHandler.TIMEOUT: timeout_handlers
            },
            fallbacks=[proxy_view_game, *unknown_handlers],
            conversation_timeout=300,
            per_message=False
        )

    handlers = [
        CommandHandler(CommandData.START, admin_santa.start),
        CommandHandler(CommandData.HELP, help_command),
        create_game_handler,
        request_description_handler,
        ConversationHandler(
            entry_points=[CallbackQueryHandler(admin_santa.request_date, CallbackData.CHANGE_DATE.regex)],
            states={
                CreateGameStates.CALENDAR: [calendar_handler]
            },
            fallbacks=[proxy_view_game, *unknown_handlers],
            conversation_timeout=300,
            per_message=True
        ),
        CommandHandler(CommandData.MY_GAMES, callback=admin_santa.my_games),
        CallbackQueryHandler(admin_santa.my_games, pattern=CallbackData.MY_GAMES.regex),
        CallbackQueryHandler(admin_santa.view_game, pattern=CallbackData.VIEW_GAME.regex),
        CallbackQueryHandler(admin_santa.shuffle_players, pattern=CallbackData.SHUFFLE_PLAYERS.regex),
        CallbackQueryHandler(admin_santa.change_registration, pattern=CallbackData.CHANGE_REGISTRATION.regex),
        CallbackQueryHandler(admin_santa.delete_game, pattern=CallbackData.DELETE_GAME.regex),
        CallbackQueryHandler(admin_santa.get_list_players, pattern=CallbackData.UPLOAD_LIST_PLAYERS.regex),
        CallbackQueryHandler(ignore_callback, pattern=CallbackData.IGNORE.regex),
        *unknown_handlers
    ]
    return handlers


def build_commands() -> list[BotCommand]:
    commands = [
        BotCommand(CommandData.START, CommandData.START.description),
        BotCommand(CommandData.HELP, CommandData.HELP.description),
        BotCommand(CommandData.CREATE_GAME, CommandData.CREATE_GAME.description),
        BotCommand(CommandData.MY_GAMES, CommandData.MY_GAMES.description),
    ]
    return commands


async def setup(app: Application):
    handlers = build_handlers()
    commands = build_commands()

    app.add_handlers(handlers)
    await app.bot.set_my_commands(commands)
