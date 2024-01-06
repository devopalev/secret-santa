from functools import partial
from datetime import date

from telegram.helpers import escape_markdown, mention_markdown

from src.domain.model import GameSanta
from src.domain.model import GameState
from src.tg.elements.base import BaseText


escape_markdown_2 = partial(escape_markdown, version=2)


class StartText(BaseText):
    def __new__(cls, fullname: str):
        return super().__new__(cls, f"Привет, {fullname}!\nИспользуй /help для вызова справки")


class GameNotFoundText(BaseText):
    def __new__(cls, many: bool = False):
        if many:
            return super().__new__(cls, "Упс, игры не найдены")
        else:
            return super().__new__(cls, "Упс, не нашел игру")


class BadLinkToGameText(BaseText):
    def __new__(cls):
        return super().__new__(cls, "Некорректная ссылка, игра не найдена")


class RegistrationClosedText(BaseText):
    def __new__(cls):
        return super().__new__(cls, "Регистрация в игре уже закрыта, обратитесь к создателю игры")


class JoinedGameText(BaseText):
    def __new__(cls, title: str):
        text = escape_markdown(f"Вы присоединились к игре {title}")
        return super().__new__(cls, text)


class AlreadyJoinedGameText(BaseText):
    def __new__(cls, title: str):
        text = escape_markdown(f"Вы уже присоединились к игре {title}")
        return super().__new__(cls, text)


class ViewGameText(BaseText):
    def __new__(cls, game: GameSanta, bot_link: str, user_id: int):
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

        text = template.format(title=title, description=description, recipient_gift=recipient_gift, status=status,
                               date=date, initiator=initiator, link=link, quantity=quantity)
        return super().__new__(cls, text)


class MyGamesText(BaseText):
    def __new__(cls):
        return super().__new__(cls, "Ваши игры\n\U0001F511 - вы владелец\n\U0001F385 - вы участник")


class RequestDescriptionGame(BaseText):
    def __new__(cls):
        text = ("Напиши понятное твоей команде описание игры, можешь указать место встречи "
                "и любую дополнительную информацию")
        return super().__new__(cls, text)


class RequestDateGame(BaseText):
    def __new__(cls):
        text = "Выбери дату вручения подарков, а я напомню всем участникам заранее"
        return super().__new__(cls, text)


class RequestTitleGame(BaseText):
    def __new__(cls):
        text = "Самое время создать новую игру \U0001F642\nНапиши название игры"
        return super().__new__(cls, text)


class DeleteGameInitiator(BaseText):
    def __new__(cls, title: str):
        title = escape_markdown_2(title)
        text = f"Игра {title} удалена! Уведомления участникам отправлены"
        return super().__new__(cls, text)


class DeleteGamePlayer(BaseText):
    def __new__(cls, title: str, user_id: int, fullname: str):
        initiator = mention_markdown(user_id, fullname, 2)
        title = escape_markdown_2(title)
        text = f"Игра {title} удалена инициатором {initiator}"
        return super().__new__(cls, text)


class DateGameChanged(BaseText):
    def __new__(cls, title: str, new_date: date):
        title = escape_markdown_2(title)
        new_date = escape_markdown_2(str(new_date))
        text = f"Дата в игре {title} изменилась на {new_date}"
        return super().__new__(cls, text)


class DescriptionGameChanged(BaseText):
    def __new__(cls, title: str, new_description: str):
        title = escape_markdown_2(title)
        new_description = escape_markdown_2(new_description)
        text = f"Описание в игре {title} изменилось на _{new_description}_"
        return super().__new__(cls, text)


class EventShufflePlayersGame(BaseText):
    def __new__(cls, title: str, user_id: int, fullname: str):
        title = escape_markdown_2(title)
        recipient = mention_markdown(user_id, fullname, 2)
        text = f"В игре {title} распределены Тайные Санты\\. Вы дарите подарок пользователю {recipient}"
        return super().__new__(cls, text)


class HelpText(BaseText):
    def __new__(cls):
        text = (f"Игра Тайный Санта - это анонимный обмен подарками в группе играющих людей\n"
                f"/create_game - создать новую игру\n"
                f"/my_games - показать все игры которые вы создали и/или в которых участвуете\n\n"
                f"\U00002705 Уведомляет игроков: распределены Тайные Санты, изменено описание или дата, удалена игра\n"
                f"\U000026A0 Выгрузить список игроков может создатель который НЕ участвует в игре\n"
                f"\U000026A0 Распределить Сант можно только если игроков больше одного\n"
                f"\U000026D4 Нельзя: менять название, распределять Тайных Сант повторно")
        return super().__new__(cls, escape_markdown_2(text))


class BadCallbackText(BaseText):
    def __new__(cls):
        return super().__new__(cls, "Не удалось распознать кнопку\\, возможно она устарела")