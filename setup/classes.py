from statemachine import StateMachine, State

from .log import logger


class CurrentBotState(StateMachine):
    """
    class containing bot state
    """
    none = State('none', initial=True)
    command = State('command')
    keyboard = State('keyboard')

    go_command = none.to(command) | keyboard.to(command)
    go_keyboard = command.to(keyboard)
    go_none = command.to(none) | keyboard.to(none)

    curr_command = ''

    def on_go_command(self, message=None):
        if message:
            self.curr_command = message

    def on_go_none(self):
        self.curr_command = ''


class TeleUser:
    """
    Class for description current state bot at user
    """
    users_dict = {}

    def __init__(self, user_id):
        self.current_state = CurrentBotState()
        self.users_dict = {user_id: self}
        TeleUser._get_dict(user_id, self)

    @classmethod
    def _get_dict(cls, user_id, instance):
        cls.users_dict[user_id] = instance
        logger.info(f'Подключился новый пользователь, chat.id = {user_id}. Всего пользователей: {len(cls.users_dict)}.')
