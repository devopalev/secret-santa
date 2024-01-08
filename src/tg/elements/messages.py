from functools import partial
from datetime import date

from telegram.helpers import escape_markdown, mention_markdown

from src.domain.model import GameSanta, Player
from src.domain.model import GameState
from src.tg.elements import keyboards
from src.tg.elements.base import BaseMessage

escape_markdown_2 = partial(escape_markdown, version=2)


class StartMessage(BaseMessage):
    def __init__(self, fullname: str):
        self.text = f"Привет, {fullname}!\nИспользуй /help для вызова справки"


class GameNotFoundMessage(BaseMessage):
    def __init__(self, many: bool = False):
        if many:
            self.text = "Упс, игры не найдены"
        else:
            self.text = "Упс, не нашел игру"


class BadLinkToGameMessage(BaseMessage):
    def __init__(self):
        self.text = "Некорректная ссылка, игра не найдена"


class RegistrationClosedMessage(BaseMessage):
    def __init__(self):
        self.text = "Регистрация в игре уже закрыта, обратитесь к создателю игры"


class JoinedGameMessage(BaseMessage):
    def __init__(self, title: str):
        self.text = escape_markdown(f"Вы присоединились к игре {title}")


class AlreadyJoinedGameMessage(BaseMessage):
    def __init__(self, title: str):
        self.text = escape_markdown(f"Вы уже присоединились к игре {title}")


class ViewGameMessage(BaseMessage):
    def __init__(self, game: GameSanta, bot_link: str, user_id: int):
        template = ("*{title}*\n"
                    "_{description}_\n\n"
                    "{recipient_gift}"
                    "{status}\n"
                    "\U000023F3 Дедлайн {date}\n"
                    "\U0001F451 Инициатор {initiator}\n"
                    "\U0001F385 Зарегистрировано {quantity} игроков \n\n"
                    "*Ссылка\\-приглашение*\n"
                    "{link}")

        for player in game.players:
            if player.telegram_id == user_id and player.recipient:
                rec_link = mention_markdown(player.recipient.telegram_id, player.recipient.fullname, 2)
                recipient_gift = f"\U0001F381 Вы дарите подарок пользователю {rec_link}\n\n"
                break
        else:
            recipient_gift = ""

        status = "*Состояние*\n"
        match game.state:
            case GameState.REGISTRATION_OPEN:
                status = "\U0001F7E2 Регистрация открыта"
            case GameState.REGISTRATION_CLOSE:
                status = "\U000026D4 Регистрация закрыта"
            case GameState.ALLOCATED:
                status = "\U0001F3C1 Тайные Санты распределены\\, выполнена рассылка уведомлений"

        title = escape_markdown_2(game.title)
        description = escape_markdown_2(game.description)
        date = escape_markdown_2(str(game.date_finish))
        initiator = mention_markdown(game.initiator_id, game.initiator_fullname, 2)
        link = escape_markdown_2(f"{bot_link}?start={game.uuid}")
        quantity = str(len(game.players))

        self.text = template.format(title=title, description=description, recipient_gift=recipient_gift, status=status,
                                    date=date, initiator=initiator, link=link, quantity=quantity)
        self.reply_markup = keyboards.ViewGameKeyboard(game, user_id)


class MyGamesMessage(BaseMessage):
    def __init__(self, games: list[GameSanta], user_id: int):
        self.text = "Ваши игры\n\U0001F511 - вы владелец\n\U0001F385 - вы участник"
        self.reply_markup = keyboards.MyGamesKeyboard(games, user_id)


class RequestDescriptionGameMessage(BaseMessage):
    def __init__(self, game: GameSanta = None):
        self.text = ("Напиши понятное твоей команде описание игры, можешь указать место встречи "
                     "и любую дополнительную информацию")
        self._game = game

    @property
    def reply_markup(self):
        assert self._game
        return keyboards.PrevViewGame(self._game)


class RequestDateGameMessage(BaseMessage):
    def __init__(self):
        self.text = "Выбери дату вручения подарков, а я напомню всем участникам заранее"


class RequestTitleGameMessage(BaseMessage):
    def __init__(self):
        self.text = "Самое время создать новую игру \U0001F642\nНапиши название игры"


class DeleteGameInitiatorMessage(BaseMessage):
    def __init__(self, title: str):
        title = escape_markdown_2(title)
        self.text = f"Игра {title} удалена! Уведомления участникам отправлены"


class DeleteGamePlayerMessage(BaseMessage):
    def __init__(self, title: str, user_id: int, fullname: str):
        initiator = mention_markdown(user_id, fullname, 2)
        title = escape_markdown_2(title)
        self.text = f"Игра {title} удалена инициатором {initiator}"


class DateGameChangedMessage(BaseMessage):
    def __init__(self, title: str, new_date: date):
        title = escape_markdown_2(title)
        new_date = escape_markdown_2(str(new_date))
        self.text = f"Дата в игре {title} изменилась на {new_date}"


class DescriptionGameChangedMessage(BaseMessage):
    def __init__(self, title: str, new_description: str):
        title = escape_markdown_2(title)
        new_description = escape_markdown_2(new_description)
        self.text = f"Описание в игре {title} изменилось на _{new_description}_"


class EventShufflePlayersGameMessage(BaseMessage):
    def __init__(self, title: str, player: Player):
        title = escape_markdown_2(title)
        recipient = mention_markdown(player.recipient.telegram_id, player.recipient.fullname, 2)
        rec_username = "@" + player.recipient.username if player.recipient.username else ""
        self.text = (f"В игре {title} распределены Тайные Санты\\. "
                     f"Вы дарите подарок пользователю {recipient} ") + rec_username


class HelpMessage(BaseMessage):
    def __init__(self):
        text = (f"Игра Тайный Санта - это анонимный обмен подарками в группе играющих людей\n"
                f"/create_game - создать новую игру\n"
                f"/my_games - показать все игры которые вы создали и/или в которых участвуете\n\n"
                f"\U00002705 Уведомляет игроков: распределены Тайные Санты, изменено описание или дата, удалена игра\n"
                f"\U000026A0 Выгрузить список игроков может создатель который НЕ участвует в игре\n"
                f"\U000026A0 Распределить Сант можно только если игроков больше одного\n"
                f"\U000026D4 Нельзя: менять название, распределять Тайных Сант повторно")
        self.text = escape_markdown_2(text)


class BadCallbackMessage(BaseMessage):
    def __init__(self):
        self.text = "Не удалось распознать кнопку\\, возможно она устарела"
