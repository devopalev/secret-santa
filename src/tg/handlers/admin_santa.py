import logging

from telegram import Update
from telegram.ext import ConversationHandler

from src.core.config import LIMIT_DESCRIPTION_GAME
from src.domain.model import GameSanta, Player, GameState
from src.tg.elements import keyboards
from src.tg.elements import messages
from src.tg.utils.context import CustomContext

from src.tg.utils.tg_calendar import TgCalendarKeyboard
from src.tg.utils.tg_calendar import Locale
from src.tg.handlers.common import CreateGameStates


logger = logging.getLogger(__name__)


async def start(update: Update, context: CustomContext) -> None:
    await update.message.reply_text(messages.StartText(update.effective_user.full_name))

    if len(context.args) == 1:
        game_id = context.args[0]
        game = await context.db_storage.get(game_id)

        if game:
            if game.check_member(update.effective_user.id):
                text = messages.AlreadyJoinedGameText(game.title)
                await update.effective_chat.send_message(text, text.parse_mode)
            elif game.state == GameState.REGISTRATION_OPEN:
                player = Player.build_from_user(update.effective_user)
                game.add_player(player)
                await context.db_storage.save(game)
                text = messages.JoinedGameText(game.title)
                await update.effective_chat.send_message(text, text.parse_mode)
                await view_game(update, context, game)
            else:
                text = messages.RegistrationClosedText()
                await update.effective_chat.send_message(text, text.parse_mode)
        else:
            text = messages.BadLinkToGameText()
            await update.effective_chat.send_message(text, text.parse_mode)


async def my_games(update: Update, context: CustomContext):
    games = await context.db_storage.get_list(telegram_id=update.effective_user.id)

    if not games:
        await update.effective_chat.send_message(messages.GameNotFoundText(many=True))
        return

    text = messages.MyGamesText()
    keyboard = keyboards.MyGamesKeyboard(games, update.effective_user.id)

    send = update.effective_message.edit_text if update.callback_query else update.effective_chat.send_message
    await send(text, reply_markup=keyboard)


async def view_game(update: Update, context: CustomContext, game: GameSanta = None):
    if not game:
        game = await context.db_storage.get(context.game_id)

        if not game:
            await update.callback_query.answer(messages.GameNotFoundText(many=False))
            return await my_games(update, context)

    text = messages.ViewGameText(game, context.bot.link, update.effective_user.id)
    is_admin = update.effective_user.id == game.initiator_id
    is_member = game.check_member(update.effective_user.id)
    keyboard = keyboards.ViewGameKeyboard(game, is_admin, is_member)

    send = update.effective_message.edit_text if update.callback_query else update.effective_chat.send_message
    await send(text, text.parse_mode, reply_markup=keyboard)


async def shuffle_players(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        game.shuffle()
        await context.db_storage.save(game)
        await view_game(update, context, game)

        for player in game.players:
            text = messages.EventShufflePlayersGame(game.title, player.recipient.telegram_id, player.recipient.fullname)
            context.send_event(text, [player])
    else:
        await update.callback_query.answer(messages.GameNotFoundText(many=False))


async def request_description(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)

    if game:
        context.game = game
        text = messages.RequestDescriptionGame()
        keyboard = keyboards.PrevViewGame(game)
        await update.callback_query.edit_message_text(text,  text.parse_mode, reply_markup=keyboard)
        return CreateGameStates.DESCRIPTION
    else:
        await update.callback_query.answer(messages.GameNotFoundText(many=False))


async def change_description(update: Update, context: CustomContext):
    context.game.description = update.effective_message.text[:LIMIT_DESCRIPTION_GAME]
    await context.db_storage.save(context.game)
    await view_game(update, context, game=context.game)
    event = messages.DescriptionGameChanged(context.game.title, context.game.description)
    context.send_event(event, context.game.players)
    return ConversationHandler.END


async def proxy_view_game(update: Update, context: CustomContext):
    del context.game
    await view_game(update, context)


async def change_registration(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        game.change_registration()
        await context.db_storage.save(game)
        await view_game(update, context, game)
    else:
        await update.callback_query.answer(messages.GameNotFoundText(many=False))


async def request_date(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)

    if game:
        await update.callback_query.answer()
        context.game = game
        cal = TgCalendarKeyboard(locale=Locale.ru)
        text = messages.RequestDateGame()
        await update.callback_query.edit_message_text(text, reply_markup=cal.keyboard)
        return CreateGameStates.CALENDAR
    else:
        await update.callback_query.answer(messages.GameNotFoundText(many=False))


async def delete_game(update: Update, context: CustomContext):
    game = await context.db_storage.get(context.game_id)
    if game:
        await context.db_storage.delete(game)
        await update.callback_query.edit_message_text(messages.DeleteGameInitiator(game.title))
        text = messages.DeleteGamePlayer(game.title, game.initiator_id, game.initiator_fullname)
        context.send_event(text, game.players)
    else:
        await update.callback_query.answer(messages.GameNotFoundText(many=False))


async def get_list_players(update: Update, context: CustomContext):
    bytes_io = await context.db_storage.get_players_csv(context.game_id)
    if bytes_io:
        await update.effective_chat.send_document(bytes_io, filename="players.csv")
    await update.callback_query.answer()
