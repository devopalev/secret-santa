import logging

from telegram import Update
from telegram.ext import ConversationHandler

from src.core.config import LIMIT_DESCRIPTION_GAME
from src.domain.model import GameSanta, Player, GameState
from src.tg.elements import messages
from src.tg.utils.context import CustomContext

from src.tg.utils.tg_calendar import TgCalendarKeyboard
from src.tg.utils.tg_calendar import Locale
from src.tg.handlers.common import CreateGameStates


logger = logging.getLogger(__name__)


async def start(update: Update, context: CustomContext) -> None:
    msg = messages.StartMessage(update.effective_user.full_name)
    await update.message.reply_text(msg.text)

    if len(context.args) == 1:
        game_id = context.args[0]
        game = await context.db_storage.get(game_id)

        if game:
            if game.check_member(update.effective_user.id):
                msg = messages.AlreadyJoinedGameMessage(game.title)
                await update.effective_chat.send_message(msg.text, msg.parse_mode)
            elif game.state == GameState.REGISTRATION_OPEN:
                player = Player.build_from_user(update.effective_user)
                game.add_player(player)
                await context.db_storage.save(game)
                msg = messages.JoinedGameMessage(game.title)
                await update.effective_chat.send_message(msg.text, msg.parse_mode)
                await view_game(update, context, game)
            else:
                msg = messages.RegistrationClosedMessage()
                await update.effective_chat.send_message(msg.text, msg.parse_mode)
        else:
            msg = messages.BadLinkToGameMessage()
            await update.effective_chat.send_message(msg.text, msg.parse_mode)


async def my_games(update: Update, context: CustomContext):
    games = await context.db_storage.get_list(telegram_id=update.effective_user.id)

    if not games:
        msg = messages.GameNotFoundMessage(many=True)
        await update.effective_chat.send_message(msg.text)
        return

    msg = messages.MyGamesMessage(games, update.effective_user.id)
    send = update.effective_message.edit_text if update.callback_query else update.effective_chat.send_message
    await send(msg.text, reply_markup=msg.reply_markup)


async def view_game(update: Update, context: CustomContext, game: GameSanta = None):
    if not game:
        game = await context.db_storage.get(context.game_id)

        if not game:
            msg = messages.GameNotFoundMessage(many=False)
            await update.callback_query.answer(msg.text)
            return await my_games(update, context)

    msg = messages.ViewGameMessage(game, context.bot.link, update.effective_user.id)
    send = update.effective_message.edit_text if update.callback_query else update.effective_chat.send_message
    await send(msg.text, msg.parse_mode, reply_markup=msg.reply_markup)


async def shuffle_players(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        game.shuffle()
        await context.db_storage.save(game)
        await view_game(update, context, game)

        for player in game.players:
            msg = messages.EventShufflePlayersGameMessage(game.title, player)
            context.send_event(msg, [player])
    else:
        msg = messages.GameNotFoundMessage(many=False)
        await update.callback_query.answer(msg.text)


async def request_description(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)

    if game:
        context.game = game
        msg = messages.RequestDescriptionGameMessage(game)
        await update.callback_query.edit_message_text(msg.text,  msg.parse_mode, reply_markup=msg.reply_markup)
        return CreateGameStates.DESCRIPTION
    else:
        msg = messages.GameNotFoundMessage(many=False)
        await update.callback_query.answer(msg.text)


async def change_description(update: Update, context: CustomContext):
    context.game.description = update.effective_message.text[:LIMIT_DESCRIPTION_GAME]
    await context.db_storage.save(context.game)
    await view_game(update, context, game=context.game)
    event = messages.DescriptionGameChangedMessage(context.game.title, context.game.description)
    context.send_event(event, context.game.players)
    return ConversationHandler.END


async def proxy_view_game(update: Update, context: CustomContext):
    del context.game
    await view_game(update, context)
    return ConversationHandler.END


async def change_registration(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        game.change_registration()
        await context.db_storage.save(game)
        await view_game(update, context, game)
    else:
        msg = messages.GameNotFoundMessage(many=False)
        await update.callback_query.answer(msg.text)


async def request_date(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)

    if game:
        await update.callback_query.answer()
        context.game = game
        cal = TgCalendarKeyboard(locale=Locale.ru)
        msg = messages.RequestDateGameMessage()
        await update.callback_query.edit_message_text(msg.text, reply_markup=cal.keyboard)
        return CreateGameStates.CALENDAR
    else:
        msg = messages.GameNotFoundMessage(many=False)
        await update.callback_query.answer(msg.text)


async def delete_game(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        await context.db_storage.delete(game)
        msg_initiator = messages.DeleteGameInitiatorMessage(game.title)
        await update.callback_query.edit_message_text(msg_initiator.text)
        msg_player = messages.DeleteGamePlayerMessage(game.title, game.initiator_id, game.initiator_fullname)
        context.send_event(msg_player, game.players)
    else:
        msg = messages.GameNotFoundMessage(many=False)
        await update.callback_query.answer(msg.text)


async def get_list_players(update: Update, context: CustomContext):
    bytes_io = await context.db_storage.get_players_csv(context.game_id)
    if bytes_io:
        await update.effective_chat.send_document(bytes_io, filename="players.csv")
    await update.callback_query.answer()
