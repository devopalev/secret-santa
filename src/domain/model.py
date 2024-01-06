import datetime
import random
from dataclasses import dataclass
from enum import Enum
from typing import overload
from uuid import UUID

from telegram import User
from telegram.helpers import escape_markdown, mention_markdown


class GameState(Enum):
    REGISTRATION_OPEN = 11
    REGISTRATION_CLOSE = 12
    ALLOCATED = 13

    @property
    def state_is_working(self):
        return self in {self.REGISTRATION_OPEN, self.REGISTRATION_CLOSE}

    def __int__(self):
        return self.value


class _Meta:
    """
    Используется для отслеживания изменений в repository
    """

    def __init__(self):
        self.changed_fields = set()
        self.new_players = set()
        self.shuffled_players = False


@dataclass
class Player:
    id: int
    telegram_id: int
    fullname: str
    username: str
    recipient_id: int
    game_uuid: str | None
    recipient: 'Player' = None

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def build_from_user(cls, user: User) -> 'Player':
        return cls(
            id=None,
            telegram_id=user.id,
            fullname=user.full_name,
            username=user.username,
            recipient_id=None,
            game_uuid=None
        )


class GameSanta:
    def __init__(self,
                 uuid: str | UUID,
                 state: GameState,
                 players: list[Player],
                 initiator_id: int,
                 initiator_fullname: str,
                 title: str,
                 description: str,
                 date_finish: datetime.date
                 ):
        self.meta = _Meta()
        self.uuid = str(uuid) if uuid else None

        self.state = GameState(state)
        self.players = players or []

        self.initiator_id = initiator_id
        self.initiator_fullname = initiator_fullname

        self.title = title
        self.description = description
        self.date_finish = date_finish

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.meta.changed_fields.add(key)
        super().__setattr__(key, value)

    @classmethod
    def build_from_user(cls, user: User):
        game = cls(
            uuid=None,
            state=GameState.REGISTRATION_OPEN,
            players=[],
            initiator_id=user.id,
            initiator_fullname=user.full_name,
            title=None,
            description=None,
            date_finish=None
        )
        game.meta.changed_fields.update(("state", "initiator_id", "initiator_fullname"))
        return game

    def change_registration(self):
        match self.state:
            case GameState.REGISTRATION_OPEN:
                self.state = GameState.REGISTRATION_CLOSE
            case GameState.REGISTRATION_CLOSE:
                self.state = GameState.REGISTRATION_OPEN

    def shuffle(self):
        copy_users = self.players.copy()
        random.shuffle(copy_users)

        for i in range(len(copy_users)):
            copy_users[i - 1].recipient = copy_users[i]
        self.state = GameState.ALLOCATED
        self.meta.shuffled_players = True

    def add_player(self, player: Player):
        assert self.uuid, "Save the game to the storage to get the id"
        player.game_uuid = self.uuid
        self.players.append(player)
        self.meta.new_players.add(player)

    def check_member(self, telegram_id: int):
        for player in self.players:
            if player.telegram_id == telegram_id:
                return True
        return False
