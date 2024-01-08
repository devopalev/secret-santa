import asyncio
import logging

from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ExtBot

from src.domain.model import GameSanta, Player
from src.repository import AbstractRepository, Repository, RepositoryMemory
from src.tg.elements.base import BaseMessage

KEY_STORAGE = "game"

logger = logging.getLogger(__name__)


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """Custom class for context."""

    db_storage: AbstractRepository = Repository()

    @property
    def game(self) -> GameSanta:
        return self.user_data.get(KEY_STORAGE, None)

    @game.setter
    def game(self, game: GameSanta):
        self.user_data[KEY_STORAGE] = game

    @game.deleter
    def game(self):
        self.user_data.pop(KEY_STORAGE, None)

    @property
    def game_id(self):
        return self.match.group(1)

    def send_event(self, event: BaseMessage, players: list[Player]):
        async def async_send_event(user_id: int, text: str, parse_mode: ParseMode):
            try:
                await self.bot.send_message(user_id, text, parse_mode)
            except Exception as err:
                logger.warning(f"Не удалось отправить сообщение ({text}) пользователю {user_id}: {err}", exc_info=True)

        for player in players:
            asyncio.create_task(async_send_event(player.telegram_id, event.text, event.parse_mode))


class MemoryCustomContext(CustomContext):
    db_storage: AbstractRepository = RepositoryMemory()
