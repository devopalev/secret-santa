

class AppError(Exception):
    pass


class EnvNotFoundError(AppError):
    def __init__(self, var_name: str):
        self.add_note(f"В переменных окружения не найдено <{var_name}>")
