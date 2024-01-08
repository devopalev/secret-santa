import calendar
from datetime import date, timedelta
from enum import Enum

from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton


class MonthDate:
    def __init__(self, year: int, month: int):
        self.month = int(month)
        self.year = int(year)

    def __eq__(self, other: 'MonthDate'):
        return self.year == other.year and self.month == other.month

    def __gt__(self, other: 'MonthDate'):
        if self.year != other.year:
            return self.year > other.year
        return self.month > other.month

    def build_day(self, day: int) -> date:
        return date(self.year, self.month, int(day))

    def build_prev_month(self) -> 'MonthDate':
        if self.month == 1:
            return self.__class__(self.year-1, 12)
        return self.__class__(self.year, self.month - 1)

    def build_next_month(self) -> 'MonthDate':
        if self.month == 12:
            return self.__class__(self.year + 1, 1)
        return self.__class__(self.year, self.month + 1)


class Locale(str, Enum):
    ru = 'ru'
    en = 'en'


_WEEK = {
    Locale.ru: ['Пн', 'Чт', 'Ср', 'Вт', 'Пт', 'Сб', 'Вс'],
    Locale.en: ["M", "T", "W", "T", "F", "S", "S"]
}

_MONTHS = {
    Locale.ru: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
    Locale.en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
}


class Action(str, Enum):
    CHANGE_MONTH = "c"
    SELECT = "s"
    IGNORE = "i"

    def __str__(self):
        return self.value


class CallbackBuilder:
    """
    Строитель callback_data для кнопок календаря
    """

    SPLIT_BLOCK = "?"
    SPLIT_ROOT = "/"
    SPLIT_DATA = "&"

    base_cb: str = "calendar"

    def __init__(self, action: Action, data: list = None, base_cb: str = None):
        self.base_cb = base_cb or self.base_cb
        self.action = action
        self.data = data

    def build(self) -> str:
        root = f"{self.base_cb}{self.SPLIT_ROOT}{self.action}"
        data = f"{self.SPLIT_BLOCK}{self.SPLIT_DATA.join(self.data)}" if self.data else ""
        return root + data

    @classmethod
    def parse(cls, callback_data: str):
        meta, r_data = callback_data.split(cls.SPLIT_BLOCK) if cls.SPLIT_BLOCK in callback_data else (callback_data, "")
        base_cb, raw_action = meta.split(cls.SPLIT_ROOT)
        action = Action(raw_action)
        data = (r_data.split(cls.SPLIT_DATA) if cls.SPLIT_DATA in r_data else r_data) or None
        return cls(action=action, data=data, base_cb=base_cb)


class ButtonFactory:
    """
    Фабрика кнопок клавиатуры календаря
    """

    def build_date(self, year: int, month: int, day: int) -> InlineKeyboardButton:
        cb = CallbackBuilder(action=Action.SELECT, data=[str(year), str(month), str(day)])
        return InlineKeyboardButton(str(day), callback_data=cb.build())

    def build_month(self, new_month: MonthDate, curr_month: MonthDate):
        assert new_month != curr_month
        cb = CallbackBuilder(action=Action.CHANGE_MONTH, data=[str(new_month.year), str(new_month.month)])
        return InlineKeyboardButton(">>>" if new_month > curr_month else "<<<", callback_data=cb.build())

    def build_title(self, year: int, month: int, locale: Locale) -> InlineKeyboardButton:
        cb = CallbackBuilder(action=Action.IGNORE)
        return InlineKeyboardButton(f"{_MONTHS[locale][month - 1]} {year}", callback_data=cb.build())

    def build_ignore(self, text: str = " ") -> InlineKeyboardButton:
        cb = CallbackBuilder(action=Action.IGNORE)
        return InlineKeyboardButton(text, callback_data=cb.build())


class TgCalendarKeyboard:
    def __init__(self,
                 min_date: date = None,
                 max_date: date = None,
                 locale: Locale = Locale.ru):
        self.min_date = min_date or date.today()
        self.max_date = max_date or self.min_date + timedelta(days=90)
        assert self.max_date > self.min_date

        self.locale = Locale(locale)

        self._selected_date: date = None

        target = self.min_date + timedelta(days=1)
        self._selected_month = MonthDate(target.year, target.month)

    @property
    def selected_date(self) -> date:
        return self._selected_date

    @property
    def keyboard(self) -> InlineKeyboardMarkup:
        # Подготовка
        factory_b = ButtonFactory()
        month_list = calendar.monthcalendar(self._selected_month.year, self._selected_month.month)

        # Шапка календаря
        keyboard = [
            [factory_b.build_title(self._selected_month.year, self._selected_month.month, self.locale)],  # 2023 12
            [factory_b.build_ignore(w) for w in _WEEK[self.locale]]                                       # Пн, Вт, Ср..
        ]

        # Тело календаря
        for week in month_list:
            week_keys = []
            for day_key in week:
                if day_key and (self.min_date < self._selected_month.build_day(day_key) <= self.max_date):
                    button = factory_b.build_date(self._selected_month.year, self._selected_month.month, day_key)
                else:
                    button = factory_b.build_ignore()
                week_keys.append(button)
            keyboard.append(week_keys)

        # Подвал календаря
        if self._selected_month > MonthDate(self.min_date.year, self.min_date.month):
            new_month = self._selected_month.build_prev_month()
            prev_key = factory_b.build_month(new_month, self._selected_month)
        else:
            prev_key = factory_b.build_ignore()

        if self._selected_month < MonthDate(self.max_date.year, self.max_date.month):
            new_month = self._selected_month.build_next_month()
            next_key = factory_b.build_month(new_month, self._selected_month)
        else:
            next_key = factory_b.build_ignore()
        keyboard.append([prev_key, next_key])

        return InlineKeyboardMarkup(keyboard)

    def handle(self, callback_data: str) -> bool:
        """
        Обработчик обратного вызова. Меняет состояние объекта.

        :param callback_data: данные обратного вызова, например base_callback/action?data1&data2&data3
        :return: True - состояние изменилось
        """
        cb = CallbackBuilder.parse(callback_data)

        match cb.action:
            case Action.CHANGE_MONTH:
                self._selected_month = MonthDate(*map(int, cb.data))
            case Action.SELECT:
                self._selected_date = date(*map(int, cb.data))

        return cb.action != Action.IGNORE


__all__ = [
    "Locale",
    "CallbackBuilder",
    "TgCalendarKeyboard"
]
