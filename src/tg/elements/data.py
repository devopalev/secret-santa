import enum

RE_GAME_ID = r"\w+-\w+-\w+-\w+-\w+"


class CommandData(str, enum.Enum):
    START = "start"
    HELP = "help"
    CREATE_GAME = "create_game"
    MY_GAMES = "my_games"

    def __str__(self):
        return self.value

    @property
    def description(self):
        match self:
            case self.START:
                return "Запустить бота"
            case self.HELP:
                return "Справка"
            case self.CREATE_GAME:
                return "Создать новую игру Тайный Санта"
            case self.MY_GAMES:
                return "Мои игры"


class CallbackData(str, enum.Enum):
    MY_GAMES = CommandData.MY_GAMES
    VIEW_GAME = "view_game"
    SHUFFLE_PLAYERS = "shuffle_players"
    CHANGE_REGISTRATION = "change_registration"
    CHANGE_DESCRIPTION = "change_description_game"
    CHANGE_DATE = "change_date_game"
    UPLOAD_LIST_PLAYERS = "upload_list_players"
    DELETE_GAME = "delete_game"
    IGNORE = "ignore"
    UNKNOWN = ".*"

    def __str__(self):
        return self.value

    @property
    def regex(self):
        r"""

        :return: VIEW_GAME: view_game=(\w+-\w+-\w+-\w+-\w+)
        """
        match self:
            case self.VIEW_GAME | self.SHUFFLE_PLAYERS | self.CHANGE_REGISTRATION | self.CHANGE_DESCRIPTION | \
                 self.CHANGE_DATE | self.UPLOAD_LIST_PLAYERS | self.DELETE_GAME:
                reg = self + f"=({RE_GAME_ID})"
            case _:
                reg = self
        return "^" + reg + "$"
