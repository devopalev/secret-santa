from telegram import InlineKeyboardMarkup

from src.domain.model import GameSanta, GameState
from src.tg.elements import buttons


class ViewGameKeyboard(InlineKeyboardMarkup):
    def __init__(self, game: GameSanta, user_id: int):
        keyboard = []

        if game.initiator_id == user_id:
            if len(game.players) > 1 and game.state != GameState.ALLOCATED:
                keyboard.append([buttons.ShufflePlayersButton(game.uuid)])
            if game.state.state_is_working:
                keyboard.append([buttons.ChangeStateButton(game)])
            keyboard.append([buttons.ChangeDescriptionButton(game.uuid)])
            keyboard.append([buttons.ChangeDateButton(game.uuid)])
            if game.players and not game.check_member(user_id):
                keyboard.append([buttons.UploadPlayersButton(game.uuid)])
            keyboard.append([buttons.DeleteGameButton(game.uuid)])
        keyboard.append([buttons.MyGamesButton(True)])
        super().__init__(keyboard)


class MyGamesKeyboard(InlineKeyboardMarkup):
    def __init__(self, games: list[GameSanta], user_id: int):
        keyboard = [[buttons.ViewGameButton(game, user_id)] for game in games]
        super().__init__(keyboard)


class PrevViewGame(InlineKeyboardMarkup):
    def __init__(self, game: GameSanta):
        keyboard = [[buttons.ViewGameButton(game, prev_emoji=True)]]
        super().__init__(keyboard)
