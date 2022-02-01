from typing import Optional

import telebot

from .all_commands import check_num, return_hotels
from .log import logger, my_log
from .const import bot
from .classes import TeleUser
from .handlers import change_state


@my_log
def take_min_price(call):
    TeleUser.users_dict[call.message.chat.id].current_state.go_command()
    logger.info(f'Бот чата {call.message.chat.id} перешел в состояние command')
    hotel_id = call.data
    bot.send_message(call.message.chat.id, 'Введите минимальную цену в долларах (целое число):')
    bot.register_next_step_handler(call.message,
                                   check_num,
                                   next_func=take_max_price,
                                   hotel_id=hotel_id,
                                   calling_func=take_min_price)


@my_log
@change_state(bot)
def take_max_price(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Getting max price
    """
    min_price = message.text
    logger.info(f'Пользователь ввел минимальную цену: {min_price}')
    bot.send_message(message.chat.id, 'Введите максимальную цену в долларах (целое число):')
    kwargs['next_func'] = take_min_distance
    kwargs['calling_func'] = take_max_price
    bot.register_next_step_handler(message, check_num, min_price=min_price, **kwargs)


@my_log
@change_state(bot)
def take_min_distance(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Getting min distance to center
    """
    max_price = message.text
    logger.info(f'Пользователь ввел максимальную цену: {max_price}')
    bot.send_message(message.chat.id, 'Введите минимальное расстояние до цента в километрах (целое число):')
    kwargs['next_func'] = take_max_distance
    kwargs['calling_func'] = take_min_distance
    bot.register_next_step_handler(message, check_num, max_price=max_price, **kwargs)


@my_log
@change_state(bot)
def take_max_distance(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Getting max distance to center
    """
    min_distance = message.text
    logger.info(f'Пользователь ввел минимальное расстояние: {min_distance}')
    bot.send_message(message.chat.id, 'Введите максимальное расстояние до цента в километрах (целое число):')
    kwargs['next_func'] = take_hotels_num
    kwargs['calling_func'] = take_max_distance
    bot.register_next_step_handler(message, check_num, min_distance=min_distance, **kwargs)


@my_log
@change_state(bot)
def take_hotels_num(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Getting amount of hotels
    """
    max_distance = message.text
    logger.info(f'Пользователь ввел максимальное расстояние: {max_distance}')
    bot.send_message(message.chat.id, 'Сколько результатов вывести (максимум 25):')
    kwargs['next_func'] = return_hotels
    kwargs['calling_func'] = take_hotels_num
    bot.register_next_step_handler(message, check_num, max_distance=max_distance, **kwargs)
