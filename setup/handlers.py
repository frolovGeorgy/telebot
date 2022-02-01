import functools
from typing import Optional, Callable, Any

import telebot

from .log import my_log, logger
from .classes import TeleUser


@my_log
def change_state(my_bot: Optional[telebot.TeleBot]) -> Callable:
    """
    Wrapper checking inputs data for correctness
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            message = args[0]
            chat_id = message.chat.id

            try:

                # checking for non-text
                if message.content_type != 'text' and TeleUser.users_dict[chat_id].current_state.is_command:
                    logger.info(f'Сработал обработчик: пользователь ввел {message.content_type}, ожидался text')
                    new_message = my_bot.send_message(chat_id, 'Пожалуйста, введите текст:')
                    my_bot.register_next_step_handler(new_message, wrapped, *args[1:])

                # checking for non-text
                elif message.content_type != 'text' and TeleUser.users_dict[chat_id].current_state.is_keyboard:
                    logger.info(f'Сработал обработчик: пользователь ввел {message.content_type}, ожидался text')
                    new_message = my_bot.send_message(chat_id, 'Пожалуйста, выберите город из списка:')
                    my_bot.register_next_step_handler(new_message, wrapped, *args[1:])

                # handler for command '/stop'
                elif message.text == '/stop' and not TeleUser.users_dict[chat_id].current_state.is_none:
                    logger.info(f'Сработал обработчик: пользователь ввел команду /stop, '
                                f'функция {func.__name__} остановлена')
                    my_bot.send_message(chat_id, 'Действие остановлено.')
                    TeleUser.users_dict[chat_id].current_state.go_none()


                else:
                    logger.info(f'Обработчик просто вернул декорируемую функцию.')
                    return func(*args, **kwargs)

            except Exception as e:
                logger.error(f'Произошла ошибка в обработчике при вызове функции {func.__name__}. {e}')
                my_bot.send_message(chat_id, 'Что-то пошло не так. Текущее действие остановлено.')
                TeleUser.users_dict[chat_id].current_state.go_none()

        return wrapped

    return decorator


@my_log
def handler_for_command(message: Optional[telebot.types.Message]) -> bool:
    """
    Filtering messages when nothing happens
    """
    user_chat_id = message.chat.id
    curr_command = message.text[1:]

    if user_chat_id not in TeleUser.users_dict:
        TeleUser(user_chat_id)
        TeleUser.users_dict[user_chat_id].current_state.go_command(message=curr_command)
        logger.info(f'Бот чата {user_chat_id} перешел в состояние command')
        return True

    elif TeleUser.users_dict[user_chat_id].current_state.is_none:
        TeleUser.users_dict[user_chat_id].current_state.go_command(message=curr_command)
        logger.info(f'Бот чата {user_chat_id} перешел в состояние command')
        return True


@my_log
def handler_for_keyboard_in_low_high(call: Optional[telebot.types.CallbackQuery]) -> bool:
    """
    Ignoring call from user keyboard while user bot is not in 'keyboard' state
    """
    if TeleUser.users_dict.get(call.message.chat.id, None):
        if TeleUser.users_dict[call.message.chat.id].current_state.curr_command in ['lowprice', 'highprice'] and \
                TeleUser.users_dict[call.message.chat.id].current_state.is_keyboard:
            return True


@my_log
def handler_for_keyboard_in_bestdeal(call: Optional[telebot.types.CallbackQuery]) -> bool:
    """
    Ignoring call from user keyboard while user bot is not in 'keyboard' state
    """
    if TeleUser.users_dict.get(call.message.chat.id, None):
        if TeleUser.users_dict[call.message.chat.id].current_state.curr_command == 'bestdeal' and \
                TeleUser.users_dict[call.message.chat.id].current_state.is_keyboard:
            return True
