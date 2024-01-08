from abc import ABC, abstractmethod

from telegram import InlineKeyboardMarkup
from telegram.constants import ParseMode


class BaseCallbackConstructor(ABC):
    @classmethod
    @abstractmethod
    def from_callback_data(cls, callback_data: str):
        ...

    @property
    @abstractmethod
    def callback_data(self):
        ...

    def __str__(self):
        return self.callback_data


class BaseText(str, ABC):
    parse_mode = ParseMode.MARKDOWN_V2


class BaseMessage(ABC):
    text: str
    parse_mode: str = ParseMode.MARKDOWN_V2
    reply_markup: InlineKeyboardMarkup = None
