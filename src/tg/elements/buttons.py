from telegram import InlineKeyboardButton

from src.tg.elements.base import BaseCallbackConstructor
from src.tg.elements.data import CallbackData
from src.domain.model import GameSanta, GameState


class CallbackGame(BaseCallbackConstructor):
    __slots__ = ["game_id", "callback"]
    splitter = "="

    def __init__(self, callback: CallbackData, game_id: str):
        self.callback = callback
        self.game_id = game_id

    @property
    def callback_data(self):
        return self.callback + self.splitter + self.game_id

    @classmethod
    def from_callback_data(cls, callback_data: str):
        return cls(*callback_data.split(cls.splitter))


class ViewGameButton(InlineKeyboardButton):
    def __init__(self, game: GameSanta, user_id: int = None, prev_emoji: bool = False):
        text_btn = game.title
        if user_id:
            text_btn = ("\U0001F511 " if game.initiator_id == user_id else "") + text_btn
            text_btn = ("\U0001F385 " if game.check_member(user_id) else "") + text_btn
        if prev_emoji:
            text_btn = "\U000021A9 " + text_btn
        super().__init__(text_btn, callback_data=str(CallbackGame(CallbackData.VIEW_GAME, game.uuid)))


class ShufflePlayersButton(InlineKeyboardButton):
    def __init__(self, game_id: str):
        super().__init__("Распределить Тайных Сант",
                         callback_data=str(CallbackGame(CallbackData.SHUFFLE_PLAYERS, game_id)))


class ChangeStateButton(InlineKeyboardButton):
    def __init__(self, game: GameSanta):
        match game.state:
            case GameState.REGISTRATION_OPEN:
                text = "Закрыть регистрацию"
            case GameState.REGISTRATION_CLOSE:
                text = "Открыть регистрацию"
            case _:
                raise ValueError(f"Недопустимое состояние игры <{game.state}>")
        super().__init__(text, callback_data=str(CallbackGame(CallbackData.CHANGE_REGISTRATION, game.uuid)))


class ChangeDescriptionButton(InlineKeyboardButton):
    def __init__(self, game_id: str):
        super().__init__("Изменить описание",
                         callback_data=str(CallbackGame(CallbackData.CHANGE_DESCRIPTION, game_id)))


class ChangeDateButton(InlineKeyboardButton):
    def __init__(self, game_id: str):
        super().__init__("Изменить дату",
                         callback_data=str(CallbackGame(CallbackData.CHANGE_DATE, game_id)))


class UploadPlayersButton(InlineKeyboardButton):
    def __init__(self, game_id: str):
        super().__init__("Выгрузить список участников",
                         callback_data=str(CallbackGame(CallbackData.UPLOAD_LIST_PLAYERS, game_id)))


class DeleteGameButton(InlineKeyboardButton):
    def __init__(self, game_id: str):
        super().__init__("Удалить игру",
                         callback_data=str(CallbackGame(CallbackData.DELETE_GAME, game_id)))


class MyGamesButton(InlineKeyboardButton):
    def __init__(self, prev_emoji: bool = False):
        text = "\U000021A9 Мои игры" if prev_emoji else "Мои игры"
        super().__init__(text, callback_data=CallbackData.MY_GAMES)
