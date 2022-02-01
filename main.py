from typing import Optional

import telebot

from setup.const import bot
from setup.log import my_log, logger
from setup.command_help import print_commands
from setup.all_commands import ask_city
from setup.low_and_high import take_hotels_num_low
from setup.bestdeal import take_min_price
from setup.handlers import handler_for_command, handler_for_keyboard_in_bestdeal, \
    handler_for_keyboard_in_low_high, change_state
from setup.classes import TeleUser


@bot.message_handler(commands=['help'])
@my_log
def help_command(message: Optional[telebot.types.Message]) -> None:
    """
    Print bot setup
    """
    print_commands(message)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'], func=handler_for_command)
@my_log
def get_name_city(message: Optional[telebot.types.Message]) -> None:
    """
    Getting the name of the city
    """
    ask_city(message)


@bot.message_handler()
@change_state(bot)
def message_filter(message: Optional[telebot.types.Message]) -> bool:
    """
    Filtering messages when keyboard is active
    """
    if TeleUser.users_dict[message.chat.id].current_state.is_keyboard:
        logger.info(f'Сработал обработчик message_filter —'
                    f' пользователь ввел текст, пока была активна клавиатура')
        bot.send_message(message.chat.id, 'Пожалуйста, выберите вариант из списка.')

        return False


@bot.callback_query_handler(func=handler_for_keyboard_in_low_high)
@bot.message_handler(func=message_filter)
@my_log
def callback_for_low_high(call: Optional[telebot.types.CallbackQuery]) -> None:
    """
    Getting amount of hotels
    """
    take_hotels_num_low(call)


@bot.callback_query_handler(func=handler_for_keyboard_in_bestdeal)
@bot.message_handler(func=message_filter)
@my_log
def callback_for_bestdeal(call: Optional[telebot.types.CallbackQuery]) -> None:
    """
    Getting min price
    """
    take_min_price(call)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
